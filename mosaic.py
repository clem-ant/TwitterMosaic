import os
import random
import itertools
from PIL import Image, ImageDraw
import numpy as np


################################################################
#                           CONFIGURATION
twitter_name = 'SamuelEtienne'

nbr_pic_per_line = 100 #Nombre de pp par ligne et col pour le résultat final
resize = 500           #Taille finale (si < 0 alors aucun resize d'appliqué)
rdm=5                  # si > 0, alors Randomise pour eviter les répétitions
uniq=False             #Mode unique (fonctionne bien avec BEAUCOUP de pp seulement)
################################################################






'''
Genere les coordonées en partant du centre
'''
def coords_from_middle(x_count, y_count):
    x_mid = int(x_count/2)
    y_mid = int(y_count/2)
    coords = list(itertools.product(range(x_count), range(y_count)))
    coords.sort(key=lambda c: abs(c[0]-x_mid) + abs(c[1]-y_mid))
    return coords


'''
Pour chaque pp de followers on lui assigne sa couleur moyenne
Retourne un dico fichier -> couleur moyenne
'''
def build_avg(directory):
    followers_avg = {}

    for file in os.listdir(directory):
        if(file.endswith('.jpg') or file.endswith('.png')):
            im = Image.open(directory+'/'+file).convert('RGB')
            follower_pp = np.array(im)
            avg = np.average(np.average(follower_pp, axis=0), axis=0).astype(int)
            followers_avg[file] = avg
    return followers_avg



'''
Calcul la couleur moyenne d'une section de l'image principale
'''
def average_section(xind, yind, size, img):
    xStart = int(xind*size)
    xEnd = int(xind*size+size)
    yStart = int(yind*size)
    yEnd = int(yind*size+size)

    nbrPxl = (xEnd-xStart)*(yEnd-yStart)
    pix = np.array([0,0,0])
    for x in range(xStart, xEnd):
        for y in range(yStart, yEnd):
            pix = np.add(pix, img[y, x])

    return (pix/(nbrPxl)).astype(int)



'''
Retourne une pp qui correspond le plus à une moyenne
rdm > 0 pour randomiser (eviter d'avoir trop de repetitions)
'''
def get_match(avg, followers_avg, rdm=1):
    values = np.array(list(followers_avg.values()))
    keys = list(followers_avg.keys())
    index = np.argsort(np.add.reduce(np.abs(np.subtract(values, avg)), axis=1))[random.randint(0, rdm)]
    return keys[index]



def create_img(twitter_name, nbr_pic, resize=0, rdm=1, uniq=False):
    followers_avg = build_avg(twitter_name)
    im_origin = Image.open(twitter_name+'.png')
    large_size, _ = im_origin.size

    if(large_size < nbr_pic):
        im_origin = im_origin.resize((nbr_pic, nbr_pic), Image.ANTIALIAS)
        large_size = nbr_pic
    user_pp = np.array(im_origin)

    small_size = 48

    section_size =large_size/nbr_pic
    final_size = nbr_pic*small_size

    img = Image.new('RGB', (final_size, final_size))

    section_list = coords_from_middle(nbr_pic, nbr_pic)

    for section in section_list:
        xSection, ySection = section[0], section[1]
        avg = average_section(xSection, ySection, section_size, user_pp)
        match = get_match(avg, followers_avg, rdm)
        if(uniq):
            followers_avg.pop(match)

        im_f = Image.open(twitter_name+'/'+match).convert('RGB').resize((small_size,small_size))
        coords = xSection*small_size, ySection*small_size
        img.paste(im_f, coords)

        if(len(followers_avg) < 1):
            break

    if(resize > 0):
        img = img.resize((resize,resize), Image.ANTIALIAS)
    img.save(twitter_name+'_output.png')


create_img(twitter_name, nbr_pic_per_line, resize, rdm, uniq)
