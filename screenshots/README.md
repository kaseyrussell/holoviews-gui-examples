I made gifs using
ffmpeg -i <fname>.mov -pix_fmt rgb24 -r 20 -f gif - | gifsicle --optimize=3 --delay=3 > <fname>.gif
