import pickle

with open('../models/lin_reg.bin', 'rb') as f_in:
    dv, model = pickle.load(f_in)