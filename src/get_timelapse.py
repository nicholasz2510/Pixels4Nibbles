import pickle

data = []
with open("history/history.pkl", 'rb') as f:
    try:
        while True:
            data.append(pickle.load(f))
    except EOFError:
        pass

for board_state in data:
    print(board_state)
