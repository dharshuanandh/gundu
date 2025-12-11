import pickle, json, os
p='data/encodings.pkl'
if not os.path.exists(p):
    print('encodings.pkl not found')
    raise SystemExit(0)
with open(p,'rb') as f:
    data=pickle.load(f)
print('entries:', len(data))
for e in data[-5:]:
    print(json.dumps({'file':e.get('file'),'encoding_len':len(e.get('encoding',[]))}))
