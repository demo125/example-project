import random
import numpy as np

def set_all_seeds(seed: int):
  random.seed(seed)
  np.random.seed(seed)
#   torch.manual_seed(seed)
#   torch.cuda.manual_seed(seed)
#   torch.backends.cudnn.deterministic = True