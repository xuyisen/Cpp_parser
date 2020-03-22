# Cpp_parser
基于Clang的C++语言解析器

### Requirements:

* Python 3.7.4
* LLVM,版本为最新版本
* Clang，版本为最新版本
* MySQL 5.6

### Build

* 首先安装Python的ClangAPI接口，`pip install clang`。
* 查找LLVM中的`libclang.so`共享库的路径，并更新到parser.py中的`Config.set_library_file(libclangPath)`中的`libclangPath`。
	* 例子：mac安装完llvm的路径为`/usr/local/opt/llvm/lib/libclang.dylib`
	* 例子：windows安装完llvm的路径为`D:/Program Files/LLVM/bin/libclang.dll`
* 我是用数据库保存提取的数据，也可以修改为用文件保存，具体格式详见`cpp.sql`

