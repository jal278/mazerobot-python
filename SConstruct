import glob



#env=Environment(CPPFLAGS='-I include/ -march=native -O2')
env=Environment(CPPFLAGS='-g -I include/')
env.ParseConfig('python-config --includes --libs')

allsrc=glob.glob('*.cpp')+glob.glob('*.cxx')
allsrc.remove("mazeApp.cpp")
allsrc.remove("mazeDlg.cpp")

env.Program('mazesim', allsrc,LIBS=['m','python2.7'])

allsrc.remove("neatmain.cpp")
env.SharedLibrary(target="_mazepy",source=allsrc,SHLIBPREFIX='',LIBS=['m','python2.7'])
