from dataset_controller import *
from mfcc_generater import *
from recorder import *
from KNN import *

if __name__ == '__main__':

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    FRAMERATE = 16000
    CHUNKLEN = 400

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=FRAMERATE,
                    input=True,
                    frames_per_buffer=CHUNKLEN)  # open stream and setting
    wf = wave.open('temp.wav', 'wb')  # open .wav and setting
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(FRAMERATE)

    mfcc_feat_s = KNNclass(
        loadFeat(featfilename='s_', dir='MFCC', N=70), 's')
    mfcc_feat_o = KNNclass(
        loadFeat(featfilename='o_mid_', dir='MFCC', N=50), 'o')
    mfcc_feat_ri = KNNclass(
        loadFeat(featfilename='ri_mid_', dir='MFCC', N=50), 'ri')
    mfcc_feat_t = KNNclass(
        loadFeat(featfilename='t_', dir='MFCC', N=30), 't')
    mfcc_feat_N = KNNclass(loadFeat(featfilename='N_', dir='MFCC', N=27), 'N')

    setColor('y')
    print('Listening...')
    ersColor()

    time_start = time.time()
    conf_cache = [{'s': 0.0, 'o': 0.0, 'ri': 0.0, 'N': 0.0}
                  for _ in range(100)]
    frame_index = np.arange(len(conf_cache))

    # about 2.5 secs per 100 chunks
    for _ in range(300):
        try:
            data_bytes = stream.read(CHUNKLEN)
            wf.writeframes(data_bytes)
            # array contain sigal in a frame
            data_int = np.fromstring(data_bytes, dtype=np.int16)

            vol = np.sum(np.abs(data_int))/CHUNKLEN
            conf_frame = getKNNclass(
                mfcc(data_int, FRAMERATE, numcep=17, nfilt=26)[
                    :, 1:], (mfcc_feat_s, mfcc_feat_o, mfcc_feat_ri, mfcc_feat_t, mfcc_feat_N),
                27)

            conf_cache.pop(0)
            conf_cache.append(conf_frame)

            print(sorted(conf_frame.items(),
                         key=lambda kv: (kv[1], kv[0]),
                         reverse=True)[0][0],
                  end='',
                  flush=True)

        except KeyboardInterrupt:
            break

    time_end = time.time()

    setColor('y')
    print('\nTime cost: ', end='')
    setColor('r')
    print(time_end - time_start, 's', sep=' ')
    setColor('y')
    print('Listening Complete.')
    ersColor()

    stream.stop_stream()  # close stream
    stream.close()
    p.terminate()
    wf.close()
