import clang.cindex
from clang.cindex import Index  #主要API
from clang.cindex import Config  #配置
from clang.cindex import CursorKind #索引节点类型
from clang.cindex import TypeKind #节点的语义类型
from clang.cindex import TokenKind
import argparse
import os      #遍历文件夹

global_words = {}

function_tokens = {}

functions = 0


libclangPath = r'/usr/local/opt/llvm/lib/libclang.dylib'  # 导入llvm 的lib文件
if Config.loaded == True:
    print("Config.loaded == True:")
    # pass
else:
    Config.set_library_file(libclangPath)
    print("install path")


def count_token(token_l,tokens):
    if token_l in tokens.keys():
        tokens[token_l] += 1
    else:
        tokens[token_l] = 1

def visit_function(node,min_tokens):
    '''访问函数节点'''
    if ".h" in str(node.location.file):
        return

    tokens = {}
    global functions
    functions = functions + 1
    for token in node.get_tokens():
        if token.kind == TokenKind.KEYWORD:
            count_token(str(token.spelling),tokens)
        elif token.kind == TokenKind.PUNCTUATION:
            pass
        elif token.kind == TokenKind.LITERAL:
            count_token(str(token.spelling),tokens)
        elif token.kind == TokenKind.IDENTIFIER:
            count_token(str(token.spelling),tokens)
        elif token.kind == TokenKind.COMMENT:
            pass
        else:
            print(token.kind,end=' ')
            print(token.spelling)
    if len(tokens) >= min_tokens:
        id = str(node.location.file)+":"+str(node.location.line)+":"+str(node.location.column)+"\n\n"+get_code(node)
        function_tokens[id] = tokens


def visit_root(node,min_tokens):
    '''遍历根节点'''
    try:
        if node.kind == CursorKind.FUNCTION_DECL:
            visit_function(node,min_tokens)
        else:
            for sub_node in node.get_children():
                visit_root(sub_node,min_tokens)
    except:
        pass

def parser(file_path,min_tokens):
    '''解析'''


    index = Index.create()

    tu = index.parse(file_path)

    AST_root_node = tu.cursor

    visit_root(AST_root_node,min_tokens)




def parse_file(file,min_tokens):
    '''遍历文件夹'''
    if os.path.isfile(file):
        file_temp = os.path.splitext(file)
        filename, type = file_temp
        if type == '.cpp':  # 是cpp文件
            print(file)
            parser(file,min_tokens)
    else:
        dir_or_files = os.listdir(file)
        for dir_file in dir_or_files:
            dir_file_path = os.path.join(file,dir_file) #获取路径
            if os.path.isdir(dir_file_path):       #如果是文件夹，则递归遍历
                parse_file(dir_file_path,min_tokens)
            elif os.path.isfile(dir_file_path): #如果是文件
                file_temp = os.path.splitext(dir_file_path)
                filename, type = file_temp
                if type == '.cpp':             #是cpp文件
                    print(dir_file_path)
                    parser(dir_file_path,min_tokens)


def similarity_measure(m1,m2):
    '''计算相似度的函数'''
    l1 = sum(m1.values())   # m1 函数的长度
    l2 = sum(m2.values())   # m2 函数的长度
    len = max(l1,l2)

    overlap = 0
    for s in m1.keys():
        if s in m2.keys():
            overlap = overlap + min(m1.get(s),m2.get(s))
    return float(overlap)/len

def get_code(cur):
    '''
    这里展示的是一个提取每个分词的方法。
    '''
    cursor_content = ""
    for token in cur.get_tokens():
        # 针对一个节点，调用get_tokens的方法。
        str_token = token.spelling + " "
        cursor_content = cursor_content + str_token
    return cursor_content


if __name__ == '__main__':

    arg = argparse.ArgumentParser()
    arg.add_argument('--f',help='input file or folder')
    arg.add_argument('-mt',help='minimum number of tokens for filtering',default=0)
    arg.add_argument('-mins',help='minimum similarity', default=0.7)
    arg.add_argument('-maxs',help='maximum similarity', default=1.0)
    options = arg.parse_args()
    min_tokens = int(options.mt)
    min_similarity = float(options.mins)
    max_similarity = float(options.maxs)
    parse_file(options.f, min_tokens)
    result = ''
    scores = {}
    keys = list(function_tokens.keys())
    for f1 in range(len(keys)):
        for f2 in range(f1+1,len(keys)):
            scores[keys[f1]+"\nxxxxxxxxxxxxxxxxxx\n "+keys[f2]] = similarity_measure(function_tokens[keys[f1]],function_tokens[keys[f2]])
    scores = sorted(scores.items(),key=lambda scores:scores[1],reverse=True)
    id = 1
    for p in scores:
        if p[1] >= min_similarity and p[1] <= max_similarity:
            result = result +str(id)+ ': ************************************************\n'
            result = result + p[0]+ "\n\n\nscore: "+str(p[1])+"\n\n\n"
            id = id + 1

    print(functions)

    with open("result.txt",'w') as f:
        f.write(result)
    # with open("identifier.txt",'w') as f:
    #     f.write(full_identifier)
    # m1={'a':1,'b':2,'c':3}
    # m2={'c':4,'d':4,'d':5}
    # print(similarity_measure(m1,m2))

    # print(full_identifier)
    # print(full_ast)
#
#
# node_list = []
#
# preorder_travers_AST(AST_root_node)
#
# cursor_content=""
# for token in AST_root_node.get_tokens():
# #针对一个节点，调用get_tokens的方法。
#     print(token.kind,end=' ')
#     print(token.spelling)
#
#
