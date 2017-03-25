def is_mov(name):
  return any( map(lambda x: name.endswith(x), ['mp4','avi','mkv'] ) )
