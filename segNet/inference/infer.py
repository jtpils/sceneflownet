from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import os
import time
import sys

def nms(pred_feat,pred_r,pred_s,dim):
  """
  dets = [x,r,s]
  """
  feat = np.reshape(pred_feat,(-1,dim)) 
  r = np.reshape(pred_r,(-1,))
  scores = np.reshape(pred_s,(-1,))

  index = np.where(scores > 0.45)[0]
    
  feat = feat[index]
  r = r[index]
  scores = scores[index] 
  
  order = scores.argsort()[::-1]
  keep = []
  while order.size > 0:
    i = order[0]
    tmp = feat[order[1:],:] - feat[i,:]
    inds = np.where(np.linalg.norm(feat[order,:] - feat[i,:],axis=1) > max(9 * r[i],0.000001))[0]
    diff = len(order) - len(inds)
    if diff > 10:
      keep.append(i)
    order = order[inds]
 
  index = np.array(keep).astype(np.int32)
  
  return feat[index], r[index], scores[index]   

def infer_seg(feat,r,s,pred_xyz,h=240,w=320):
  final_seg = np.zeros((h,w))
  count = 1
  instances_seg_pred = []
  instances_scores = [] 
  for ins_i in xrange(len(feat)):
    map_id = np.linalg.norm(pred_xyz - feat[ins_i], axis=2) < r[ins_i] * 9
    empty_id = final_seg < 1.0
    map_id = np.logical_and(empty_id,map_id)
    if np.sum(map_id) > 10:
      final_seg[map_id] = count 
      count += 1
      idx_mask = np.reshape(map_id,[h,w,1])
      idx_mask = idx_mask.astype(np.float32)      
      instances_seg_pred.append(idx_mask)
      instances_scores.append(s[ins_i])
  return final_seg, instances_seg_pred, instances_scores
