import pickle

data = []
with open("history/history.pkl", 'rb') as f:
    try:
        while True:
            data.append(pickle.load(f))
    except EOFError:
        pass

print("# of states stored: " + str(len(data)))
# TODO implement timelapse generation with PIL and ffmpeg
