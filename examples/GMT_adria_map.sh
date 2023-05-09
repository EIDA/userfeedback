# This is a gmt script for creating global or regional maps of seismic station event data
#
#
infile=$1.txt
infileoutlines=$1_helper.txt
infileallperm=AdAStations/perm10plus.txt
infiletempdepl=AdAStations/yesDepl.txt
infiletempnodepl=AdAStations/notDepl.txt
#infileall=AdAStations/station_list
#infile2=gmt_inventory2020_permanent.txt
#infile3=SPAIN_noANT.txt
#infile4=NORWAY.txt
#infile5=Unavailable_Permanent_Stations.txt
ps=$2.ps
cfile=cfile.cpt
gridfile=tempgrid.grd
#region=-180/180/-90/90
#region=-10/40/34/58
#region=-24/46/33.4/70
#region=0/40/33.4/55
region=0/32/33.4/51
mid=16.5
#mid=11
#mid=20
#region=$3
#mid=$4
crange=0/100/0.5
scale=20
gmt makecpt -Cred,pink,green -T$crange -i2 -Z > $cfile
#gmt makecpt -Cpolar -T$crange -i2 -Z > $cfile
#gmt xyz2grd $infile -G$gridfile -R$3 -I1
#gmt grdimage $gridfile -R$3 -JR$5/8.5i -K -C$cfile -BWseN -B5g -Ei > $ps
gmt pscoast -R$region -JR$mid/8.6i -Na/white -K -Dh -Sgrey20 -Ggrey40 -Wthinnest -B+t"" > $ps
#gmt grdimage $infile -R -J -O -K -Sc -C$cfile >> $ps
#gmt psxy $infile3 -R -J -O -K -St0.13 -Cwhite >> $ps
#gmt psxy $infile5 -R -J -O -K -St0.13 -Cwhite >> $ps
#gmt psxy $infile2 -R -J -O -K -St0.13 -Cwhite >> $ps
#gmt psxy $infile4 -R -J -O -K -St0.13 -Cwhite >> $ps
gmt psxy $infiletempnodepl -R -J -O -K -St0.16 -Cwhite -Wblack >> $ps
gmt psxy $infiletempdepl -R -J -O -K -St0.16 -Cblack -Wwhite >> $ps
gmt psxy $infileallperm -R -J -O -K -St0.16 -Cblack -Wwhite >> $ps
gmt psxy $infileoutlines -R -J -O -K -St -Cblack -Wblack >> $ps
gmt psxy $infile -R -J -O -K -St -C$cfile >> $ps
#gmt psxy $event_file -R -J -O -K -Sa0.45 -W1p -Cblack >> $ps
#gmt psxy $event_file -R -J -O -K -Sa0.3 -Wthick,yellow -Cblack >> $ps
#gmt psxy circle2.txt -R -J -O -K -Sp0.1 -W1p >> $ps
#gmt psxy circle2.txt -R -J -O -K -Se -W1p >> $ps
#gmt psscale -O -R -J -K -Dn0.05/-0.02+w8i/0.25i+h -C$cfile -Bx$scale+l'availability [%]' >> $ps
#gmt psscale -O -R -J -K -Dn0.05/-0.02+w8i/0.25i+h -C$cfile -Bx$scale+l'variability [%]' >> $ps
gmt psscale -O -R -J -K -Dn0.05/-0.02+w8i/0.25i+h -C$cfile -Bx$scale+l'availability [%]' >> $ps
#gmt psscale -O -R -J -K -Dn0.05/-0.1+w8i/0.25i+h+e -C$cfile -Bx$scale+l'depth [km]' >> $ps
gmt pslegend -R -J -O -Dn-0.05/-0.25+w2.2i/1i << EOF >> $ps
C white
F grey40
S 0.1i t 0.18 black white 0.3i not available during test
C white
F grey40
S 0.1i t 0.18 white black 0.3i not deployed yet
EOF
gmt psconvert -A5p -P-V -Tg $ps
rm $ps
#./GMT_generic_map.sh '201105051657' 'h' 'Residual_[s]' 'residual' 'global' 'S' '-20/20/0.1' '0.075' '-180/180/-90/90' '0' 'c' '45' '' '5'
#./GMT_generic_map.sh '201105051657' 'h' 'Residual_[s]' 'residual' 'europe' 'S' '-20/20/0.1' '0.2' '-10/40/35/55' '15' 'h' '5' '' '5'
#./GMT_generic_map.sh '201105051657' 'h' 'Residual_[s]' 'residual' 'usa' 'S' '-20/20/0.1' '0.2' '-130/-60/25/50' '-95' 'h' '5' '' '5'
#S 0.1i t 0.18 white thinnest,black 0.3i not available during test
