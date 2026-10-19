import re,sys,glob
for f in sorted(glob.glob('/home/claude/maeumgil-cards/blog/posts/*.txt')):
  t=open(f).read().split('===',1)[1]
  t=re.sub(r'\[\d+\]','',t); t=re.sub(r'^#+ ','',t,flags=re.M); t=re.sub(r'\n+','\n',t)
  print(f.split('/')[-1],len(t.strip()), 'MMPI!' if 'MMPI' in t else '')
