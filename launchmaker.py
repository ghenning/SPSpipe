import numpy as np
import os

LoDM = str(0)
HiDM = str(1000)
FIL = "/bla/path/yay"
RESPATH = "/bla/another/path/yay"
CODEPATH = "/bla/more/paths/yay"
JOBNAME = "blabla"

def create_script(LoDM,HiDM,FILPATH,FIL,RESPATH,CODEPATH,JOBNAME):
    with open("launch_me.sh",'w') as F:
        F.write("#!/bin/bash -l \n")
        F.write("\n") 
        F.write("#SBATCH -o ./" + JOBNAME + ".err.%j \n")
        F.write("#SBATCH -D ./ \n")
        F.write("#SBATCH -J " + JOBNAME + "\n")
        F.write("#SBATCH --partition=long.q \n")
        F.write("#SBATCH --nodes=1 \n")
        F.write("#SBATCH --cpus-per-task=8 \n")
        #F.write("#SBATCH --ntasks=1 \n")
        #F.write("#SBATCH --ntasks-per-node=1 \n")
        F.write("#SBATCH --mem=15360 \n")
        F.write("#SBATCH --time=40:00:00 \n")
        F.write("\n") 
        F.write("echo \"NODE: \"$HOSTNAME \n")
        F.write("echo \"Space on node:\"\n")
        F.write("df -h \n")
        F.write("\n") 
        F.write("module load singularity \n")
        F.write("\n") 
        F.write("DDl=\"" + LoDM + "\" \n")
        F.write("DDh=\"" + HiDM + "\" \n")
        filly = os.path.join(FILPATH,FIL + ".fil")
        F.write("orig_fil=\"" + filly + "\" \n")
        #F.write("orig_fil=\"" + FIL + ".fil\" \n")
        F.write("tmpdir=\"/tmp/" + FIL + "\" \n")
        F.write("tmpfil=$tmpdir\"/" + FIL + ".fil\" \n")
        F.write("result_dir=\"" + RESPATH + "\" \n")
        F.write("code_dir=\"" + CODEPATH + "\" \n")
        F.write("\n") 
        F.write("if [ ! -d \"$tmpdir\" ]; then \n")
        F.write("\t mkdir $tmpdir \n")
        F.write("fi \n")
        F.write("\n") 
        F.write("rsync -v $orig_fil $tmpdir \n")
        F.write("\n") 
        F.write("singularity exec -B $code_dir:/work/ -B $tmpdir:/data/ -B $result_dir:/out/ /hercules/u/ghil/singularity/images/prestomod-2017-05-11-29e5097df53c.img python /work/mainpipe1bit.py --dddir /data/ --outdir /out/ --DDlo $DDl --DDhi $DDh --fil %s \n" % FIL)
        F.write("\n")
        F.write("echo \"removing temp dir on tmp: \"$tmpdir \n")
        F.write("rm -rf $tmpdir \n")
        F.write("echo \"it's gone, byebye \"$tmpdir \n")
        F.write("\n") 
        F.write("echo \"NODE: \"$HOSTNAME \n")
        F.write("echo \"Space on node:\"\n")
        F.write("df -h \n")

