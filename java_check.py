import sys, os, re
import javalang
import logging
import traceback
import itertools
import argparse

global found_parent

re_string = re.escape("\"") + '.*?' + re.escape("\"")

def getFunctions(filestring, comment_inline_pattern):

  method_string = []
  method_pos    = []
  method_name   = []

  global found_parent
  found_parent = []

  tree = None

  try:
    tree = javalang.parse.parse( filestring )
    package = tree.package
    if package is None:
      package = 'JHawkDefaultPackage'
    else:
      package = package.name
      #print package,'####'
  except Exception as e:
    #logging.warning('Traceback:' + traceback.print_exc())
    return (None, None, [])

  file_string_split = filestring.split('\n')
  nodes = itertools.chain(tree.filter(javalang.tree.ConstructorDeclaration), tree.filter(javalang.tree.MethodDeclaration))

  for path, node in nodes:
    #print '---------------------------------------'
    name = '.'+node.name
    for i, var in enumerate(reversed(path)):
      #print var, i, len(path)-3
      if isinstance(var, javalang.tree.ClassDeclaration):
        #print 'One Up:',var,var.name
        if len(path)-3 == i: #Top most
          name = '.'+var.name+check_repetition(var,var.name)+name
        else:
          name = '$'+var.name+check_repetition(var,var.name)+name
      if isinstance(var, javalang.tree.ClassCreator):
        #print 'One Up:',var,var.type.name
        name = '$'+var.type.name+check_repetition(var,var.type.name)+name
      if isinstance(var, javalang.tree.InterfaceDeclaration):
        #print 'One Up:',var,var.name
        name = '$'+var.name+check_repetition(var,var.name)+name
    #print i,var,len(path)
    #print path
    #while len(path) != 0:
    #  print path[:-1][-1]
    args = []
    for t in node.parameters:
      dims = []
      if len(t.type.dimensions) > 0:
        for e in t.type.dimensions:
          dims.append("[]")
      dims = "".join(dims)
      args.append(t.type.name+dims)
    args = ",".join(args)

    fqn = ("%s%s(%s)") % (package,name,args)
    #print "->",fqn

    (init_line,b) = node.position
    method_body = []
    closed = 0
    openned = 0

    #print '###################################################################################################'
    #print (init_line,b)
    #print 'INIT LINE -> ',file_string_split[init_line-1]
    #print '---------------------'

    for line in file_string_split[init_line-1:]:
      if len(line) == 0:
        continue
      #print '+++++++++++++++++++++++++++++++++++++++++++++++++++'
      #print line
      #print comment_inline_pattern
      line_re = re.sub(comment_inline_pattern, '', line, flags=re.MULTILINE)
      line_re = re.sub(re_string, '', line_re, flags=re.DOTALL)

      #print line
      #print '+++++++++++++++++++++++++++++++++++++++++++++++++++'

      closed  += line_re.count('}')
      openned += line_re.count('{')
      if (closed - openned) == 0:
        method_body.append(line)
        break
      else:
        method_body.append(line)

    #print '\n'.join(method_body)

    end_line = init_line + len(method_body) - 1
    method_body = '\n'.join(method_body)

    method_pos.append((init_line,end_line))
    method_string.append(method_body)

    method_name.append(fqn)

  if (len(method_pos) != len(method_string)):
    return (None,None,method_name)
  else:
    return (method_pos,method_string,method_name)

def check_repetition(node,name):
  before = -1
  i = 0
  for (obj,n,value) in found_parent:
    if obj is node:
      if value == -1:
        return ''
      else:
        return '_'+str(value)
    else:
      i += 1
    if n == name:
      before += 1
  found_parent.append((node,name,before))
  if before == -1:
    return ''
  else:
    return '_'+str(before)


#######################################################################################

function_tokens = {}

def count_token(token_l, tokens):
  if token_l in tokens.keys():
    tokens[token_l] += 1
  else:
    tokens[token_l] = 1

def similarity_measure(m1, m2):
  '''计算相似度的函数'''
  l1 = sum(m1.values())  # m1 函数的长度
  l2 = sum(m2.values())  # m2 函数的长度
  len = max(l1, l2)

  overlap = 0
  for s in m1.keys():
    if s in m2.keys():
      overlap = overlap + min(m1.get(s), m2.get(s))
  return float(overlap) / len


def parse_file(file, min_tokens):
  '''遍历文件夹'''
  if os.path.isfile(file):
    file_temp = os.path.splitext(file)
    filename, type = file_temp
    if type == '.java':  # 是java文件
      print(file)
      parser(file, min_tokens)
  else:
    dir_or_files = os.listdir(file)
    for dir_file in dir_or_files:
      dir_file_path = os.path.join(file, dir_file)  # 获取路径
      if os.path.isdir(dir_file_path):  # 如果是文件夹，则递归遍历
        parse_file(dir_file_path, min_tokens)
      elif os.path.isfile(dir_file_path):  # 如果是文件
        file_temp = os.path.splitext(dir_file_path)
        filename, type = file_temp
        if type == '.java':  # 是java文件
          print(dir_file_path)
          parser(dir_file_path, min_tokens)


def parser(file_path, min_tokens):
  '''解析'''
  f = open(file_path, 'r')
  filestring = f.read()
  (positions, strings, names) = getFunctions(filestring, "//[^\n]*")
  for i in range(len(strings)):
    my_tokens = {}
    tokens = list(javalang.tokenizer.tokenize(strings[i]))
    for token in tokens:
      if isinstance(token, javalang.tokenizer.Separator):
        pass
      elif isinstance(token, javalang.tokenizer.Operator):
        pass
      else:
        count_token(str(token.value),my_tokens)
    if len(my_tokens) >= min_tokens:
        id = file_path+":"+str(positions[i][0])+":"+str(positions[i][1])+"\n\n"+strings[i]
        function_tokens[id] = my_tokens


if __name__ == "__main__":
  # Read straight from a file, for testing purposes

  arg = argparse.ArgumentParser()
  arg.add_argument('--f', help='input file or folder')
  arg.add_argument('-mt', help='minimum number of tokens for filtering', default=0)
  arg.add_argument('-mins', help='minimum similarity', default=0.7)
  arg.add_argument('-maxs', help='maximum similarity', default=1.0)
  options = arg.parse_args()
  min_tokens = int(options.mt)
  min_similarity = float(options.mins)
  max_similarity = float(options.maxs)
  parse_file(options.f, min_tokens)
  result = ''
  scores = {}
  keys = list(function_tokens.keys())
  for f1 in range(len(keys)):
    for f2 in range(f1 + 1, len(keys)):
      scores[keys[f1] + "\nxxxxxxxxxxxxxxxxxx\n " + keys[f2]] = similarity_measure(function_tokens[keys[f1]],
                                                                                   function_tokens[keys[f2]])
  scores = sorted(scores.items(), key=lambda scores: scores[1], reverse=True)
  id = 1
  for p in scores:
    if p[1] >= min_similarity and p[1] <= max_similarity:
      result = result + str(id) + ': ************************************************\n'
      result = result + p[0] + "\n\n\nscore: " + str(p[1]) + "\n\n\n"
      id = id + 1

  with open("result.txt", 'w') as f:
    f.write(result)