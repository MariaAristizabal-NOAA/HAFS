#! /usr/bin/env python3

import os, sys, logging, glob

if 'USHhafs' in os.environ:
    sys.path.append(os.environ['USHhafs'])
elif 'HOMEhafs' in os.environ:
    sys.path.append(os.path.join(os.environ['HOMEhafs'],'ush'))
else:
    guess_HOMEhafs=os.path.dirname(os.path.dirname(
            os.path.realpath(__file__)))
    guess_USHhafs=os.path.join(guess_HOMEhafs,'ush')
    sys.path.append(guess_USHhafs)

import produtil.setup, produtil.datastore, produtil.fileop
from produtil.datastore import Datastore
from produtil.fileop import deliver_file, remove_file
import hafs.launcher, hafs.config, hafs.hycom

produtil.setup.setup()
 
environ_CONFhafs=os.environ.get('CONFhafs','NO_CONFhafs')
#conf=hafs.launcher.HAFSLauncher().read(environ_CONFhafs)
conf=hafs.launcher.load(environ_CONFhafs)

logger=conf.log('hycominit')
logger.info("hycominit1 started")

DATA=os.environ.get('DATA',conf.getloc('WORKhafs','.')+"/ocn_prep")
fcstlen=conf.getint('config','NHRS',126)
os.environ['MPISERIAL'] = conf.getloc('MPISERIAL','NONE') 
os.environ['mpiserial'] = conf.getloc('mpiserial','NONE') 

filename=DATA+"/hycominit1_state.sqlite3"
remove_file(filename)
ds=Datastore(filename,logger=logger)

hycominit1workdir=DATA+"/hycominit1"
hycominit1=hafs.hycom.HYCOMInit1(dstore=ds,conf=conf,section='hycominit1',taskname='hycominit1',workdir=hycominit1workdir,fcstlen=fcstlen)
#hycominit1.run()

COMocean = conf.getloc('COMocean')
WORKhafs = conf.getloc('WORKhafs')
hour = conf.getloc('hour')
hour_int = int(hour)
YMD = conf.getloc('YMD')
dir_mom6 = COMocean + '/' + 'mom6.' + YMD  
dir_hycominit1 = DATA + '/hycominit1'
dir_intercom = WORKhafs + '/intercom'
dir_hycominit = dir_intercom + '/hycominit'

os.system('mkdir ' + dir_hycominit1) 
os.system('mkdir ' + dir_hycominit) 

# Linking MOM6 initial condition files to hycominit1 folder 
file_restart_a = glob.glob(os.path.join(dir_mom6,'mom6_hat10*restart.a*'))[0].split('/')[-1]
file_restart_b = glob.glob(os.path.join(dir_mom6,'mom6_hat10*restart.b'))[0].split('/')[-1]
ext_restart_a = file_restart_a[-1]
ext_archv_a = glob.glob(os.path.join(dir_mom6,'mom6_hat10*archv.a*'))[0][-1]
if hour_int == 0:
    cmd = 'ln -sf ' + dir_mom6 + '/' + file_restart_a + ' ' + dir_hycominit1 + '/' +  file_restart_a
    os.system(cmd)
    cmd = 'ln -sf ' + dir_mom6 + '/' + file_restart_b + ' ' + dir_hycominit1 + '/' +  file_restart_b
    os.system(cmd)
    if ext_restart_a != 'a':
        os.chdir(dir_hycominit1)
        cmd = 'tar -xpvzf ' + file_restart_a
        os.system(cmd)
        cmd = 'cp ' + 'mom6.' + YMD + '/mom6_hat10.t12z.n00.restart.a ' + 'mom6_hat10.t00z.n00.restart.a' 
        os.system(cmd)
else:
    if ext_archv_a == 'a':
        cmd = 'ln -sf ' + dir_mom6 + '/' + 'mom6_hat10.t00z.f' + hour + '.archv.a ' + dir_hycominit1 + '/' + 'mom6_hat10.t00z.f' + hour + '.archv.a' 
        os.system(cmd)
        cmd = 'ln -sf ' + dir_mom6 + '/' + 'mom6_hat10.t00z.f' + hour + '.archv.b ' + dir_hycominit1 + '/' + 'mom6_hat10.t00z.f' + hour + '.archv.b' 
        os.system(cmd)
    else:
        cmd = 'ln -sf ' + dir_mom6 + '/' + 'mom6_hat10.t00z.f' + hour + '.archv.a.tgz ' + dir_hycominit1 + '/' + 'mom6_hat10.t00z.f' + hour + '.archv.a.tgz' 
        os.system(cmd)
        cmd = 'ln -sf ' + dir_mom6 + '/' + 'mom6_hat10.t00z.f' + hour + '.archv.b ' + dir_hycominit1 + '/' + 'mom6_hat10.t00z.f' + hour + '.archv.b' 
        os.system(cmd)
        os.chdir(dir_hycominit1)
        cmd = 'tar -xpvzf ' + 'mom6_hat10.t00z.f' + hour + '.archv.a.tgz' 
        os.system(cmd)
        cmd = 'cp ' + 'mom6.' + YMD + '/mom6_hat10.t12z.n00.restart.a ' + 'mom6_hat10.t00z.f' + hour + '.archv.a' 
        os.system(cmd)

# Writing hycom_settings file
os.chdir(dir_hycominit)
hycominit1.select_domain(logger)
hycominit1.hycom_settings.deliver(frominfo='./hycom_settings')

# Linking restart files to hycominit1 folder 
file_restart_a = glob.glob(os.path.join(dir_mom6,'mom6_hat10*restart.a*'))[0].split('/')[-1]
file_restart_b = glob.glob(os.path.join(dir_mom6,'mom6_hat10*restart.b'))[0].split('/')[-1]
ext_restart_a = file_restart_a[-1]
cmd = 'ln -sf ' + dir_mom6 + '/' + file_restart_a + ' ' + dir_hycominit1 + '/' +  file_restart_a
os.system(cmd)
cmd = 'ln -sf ' + dir_mom6 + '/' + file_restart_b + ' ' + dir_hycominit1 + '/' +  file_restart_b
os.system(cmd)

# copying restart files to hycominit folder 
cmd = 'cp ' + dir_hycominit1 + '/' + file_restart_a + ' ' + dir_hycominit + '/restart_out.a' 
os.system(cmd)
cmd = 'cp ' + dir_hycominit1 + '/' + file_restart_b + ' ' + dir_hycominit + '/restart_out.b' 
os.system(cmd)
if ext_restart_a != 'a':
    os.chdir(dir_hycominit1)
    cmd = 'tar -xpvzf ' + file_restart_a
    os.system(cmd)
    cmd = 'cp ' + 'mom6.' + YMD + '/mom6_hat10.t12z.n00.restart.a ' + dir_hycominit + '/restart_out.a'
    os.system(cmd)

logger.info("hycominit1 done")

logger.info("hycominit2 started")

filename=DATA+"/hycominit2_state.sqlite3"
remove_file(filename)
ds=Datastore(filename,logger=logger)

hycominit2workdir=DATA+"/hycominit2"
hycominit2=hafs.hycom.HYCOMInit2(dstore=ds,conf=conf,section='hycominit2',taskname='hycominit2',workdir=hycominit2workdir,fcstlen=fcstlen)
hycominit2.run()

logger.info("hycominit2 done")
