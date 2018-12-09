import sys
from getopt import gnu_getopt

if __name__ == '__main__':
    options = 'hln:s:'
    opt_arg, args =  gnu_getopt(sys.argv[1:], options)
    print(opt_arg)
    for opt, arg in opt_arg:
        print('option {}: {}'.format(opt, arg))