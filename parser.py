import clang.cindex
from clang.cindex import Index  #主要API
from clang.cindex import Config  #配置
from clang.cindex import CursorKind #索引节点类型
from clang.cindex import TypeKind #节点的语义类型
from clang.cindex import TokenKind
import os      #遍历文件夹
import pymysql

full_ast = ""
full_identifier = ""

ast = ""  # 特征2

db = pymysql.connect(host='127.0.0.1',
                     port=3306,
                     user='root',
                     password='123456',
                     db='acm')  #数据库
cs = db.cursor()

libclangPath = r'/usr/local/opt/llvm/lib/libclang.dylib'  # 导入llvm 的lib文件
if Config.loaded == True:
    print("Config.loaded == True:")
    # pass
else:
    Config.set_library_file(libclangPath)
    print("install path")

def preorder_travers_AST(cursor):
    '''前序遍历节点'''

    str_ast = str(cursor.kind).replace("CursorKind.","")    # 提取特征2
    global ast
    ast = ast + str_ast+" "
    # print(cursor.kind ,end=' ')
    # print(cursor.type.kind, end= ' ')
    # print(get_code(cursor))
    # print(iter_cursor_content(cursor))
    for cur in cursor.get_children():
        #do something
        preorder_travers_AST(cur)

def visit_function(node):
    '''访问函数节点'''
    identifier = ""  # 特征1
    global ast
    ast = ""
    if ".h" in str(node.location.file):
        return
    for token in  node.get_tokens():     # 提取特征1
        if token.kind == TokenKind.LITERAL:
            str_token = "<LITERAL> "
        elif token.kind == TokenKind.COMMENT:
            pass
        else:
            str_token = token.spelling + " "
        identifier = identifier + str_token

    preorder_travers_AST(node)  # 提取特征2

    code_sql = get_code(node)

    sql = "INSERT INTO cpp (file,line,`column`,code,identifier,ast) values(%s,%s,%s,%s,%s,%s)"
    file_sql = str(node.location.file)
    line_sql = str(node.location.line)
    column_sql = str(node.location.column)
    values = (file_sql,line_sql,column_sql,code_sql,identifier,ast)
    cs.execute(sql,values)
    db.commit()
    # print(ast)
    # print(identifier)
    print(node.location)
    print(node.location.file)
    print(node.location.line)
    print(node.location.column)
    global full_ast

    full_ast = full_ast+ast+"\n"

    global full_identifier

    full_identifier = full_identifier + identifier+"\n"

def visit_root(node):
    '''遍历根节点'''
    if node.kind == CursorKind.FUNCTION_DECL:
        visit_function(node)
    else:
        for sub_node in node.get_children():
            visit_root(sub_node)

def parser(file_path):
    '''解析'''


    index = Index.create()

    tu = index.parse(file_path)

    AST_root_node = tu.cursor


    # for token in AST_root_node.get_tokens():
    # #针对一个节点，调用get_tokens的方法。
    #     print(token.kind,end=' ')
    #     print(token.spelling)

    visit_root(AST_root_node)
    # preorder_travers_AST(AST_root_node)


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


def parse_file(file):
    '''遍历文件夹'''
    if os.path.isfile(file):
        file_temp = os.path.splitext(file)
        filename, type = file_temp
        if type == '.cpp':  # 是cpp文件
            parser(file)
    else:
        dir_or_files = os.listdir(file)
        for dir_file in dir_or_files:
            dir_file_path = os.path.join(file,dir_file) #获取路径
            if os.path.isdir(dir_file_path):       #如果是文件夹，则递归遍历
                parse_file(dir_file_path)
            elif os.path.isfile(dir_file_path): #如果是文件
                file_temp = os.path.splitext(dir_file_path)
                filename, type = file_temp
                if type == '.cpp':             #是cpp文件
                    parser(dir_file_path)


if __name__ == '__main__':
    parse_file("/Users/xuyisen/Downloads/ACM/")
    with open("ast.txt",'w') as f:
        f.write(full_ast)
    with open("identifier.txt",'w') as f:
        f.write(full_identifier)
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
