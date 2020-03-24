import ast
import os
import tokenize
import io
import token
import argparse


def getFunctions(filestring):
    tree = None
    try:
        tree = ast.parse(filestring)
    except Exception as e:
        return (None, None)

    linecount = filestring.count("\n")
    if not filestring.endswith("\n"):
        linecount += 1

    blocks_linenos = []

    # print ast.dump(tree)
    # ast.walk(tree): walk the tree recursively to find all FunctionDef,
    # but now we only need level 1 functions
    # in ast, lineno of a stmt start with 1
    for index, stmt in enumerate(tree.body):
        if isinstance(stmt, ast.ClassDef):
            for idx, s in enumerate(stmt.body):
                if isinstance(s, ast.FunctionDef):
                    start_lineno = None
                    end_lineno = None
                    # unparser = unparse.Unparser(s)
                    start_lineno = s.lineno
                    if idx == len(stmt.body) - 1:
                        # this is the last one in stmt.body
                        if index == len(tree.body) - 1:
                            # also the last stmt in tree.body
                            end_lineno = linecount
                        else:
                            # but not the last stmt in tree.body
                            end_lineno = tree.body[index + 1].lineno - 1
                    else:
                        # not the last one in stmt.body
                        end_lineno = stmt.body[idx + 1].lineno - 1
                    blocks_linenos.append((start_lineno, end_lineno))

        if isinstance(stmt, ast.FunctionDef):
            start_lineno = None
            end_lineno = None
            start_lineno = stmt.lineno
            if index == len(tree.body) - 1:
                # the last stmt in tree.body
                end_lineno = linecount
            else:
                end_lineno = tree.body[index + 1].lineno - 1
            blocks_linenos.append((start_lineno, end_lineno))

    # print blocks_linenos
    strings = [""] * len(blocks_linenos)
    for i, line in enumerate(filestring.split("\n")):
        for j, linenos in enumerate(blocks_linenos):
            if i + 1 >= linenos[0] and i + 1 <= linenos[1]:
                strings[j] += line + "\n"
    for string in strings:
        string = string[:-1]  # remove the last "\n"
    return (blocks_linenos, strings)


#####################################################################################################


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
    if type == '.py':  # 是python文件
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
        if type == '.py':  # 是python文件
          print(dir_file_path)
          parser(dir_file_path, min_tokens)


def parser(file_path, min_tokens):
  '''解析'''
  f = open(file_path, 'r')
  filestring = f.read()
  (positions, strings) = getFunctions(filestring)
  if len(strings) == 0:
      my_tokens = {}
      f = open(file_path, 'r')
      tokens = tokenize.generate_tokens(f.readline)
      for t in tokens:
          if t.type == token.ENCODING:
              pass
          elif t.type == token.OP:
              pass
          elif t.type == token.NEWLINE:
              pass
          elif t.type == token.INDENT:
              pass
          elif t.type == token.COMMENT:
              pass
          elif t.type == token.DEDENT:
              pass
          elif t.type == token.ENDMARKER:
              pass
          else:
              count_token(t.string,my_tokens)
      if len(my_tokens) >= min_tokens:
          id = file_path+ "\n\n" + filestring
          function_tokens[id] = my_tokens
  else:
      for i in range(len(strings)):
        my_tokens = {}
        tokens = tokenize.tokenize(io.BytesIO(strings[i].encode('utf-8')).readline)
        for t in tokens:
            if t.type == token.ENCODING:
                pass
            elif t.type == token.OP:
                pass
            elif t.type == token.NEWLINE:
                pass
            elif t.type == token.INDENT:
                pass
            elif t.type == token.COMMENT:
                pass
            elif t.type == token.DEDENT:
                pass
            elif t.type == token.ENDMARKER:
                pass
            else:
                count_token(t.string,my_tokens)
        if len(my_tokens) >= min_tokens:
            id = file_path + ":" + str(positions[i][0]) + ":" + str(positions[i][1]) + "\n\n" + strings[i]
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
