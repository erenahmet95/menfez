def menfez():

    x=int(input("Menfez Genişlik mesafeeini Giriniz"))

    y= int(input("Menfez Boyunu Giriniz"))

    z = int(input("Menfez Yükseklik Değerini Giriniz"))

    X_noktaları = [[0,0,x,x],[x,x,x,x],[x,x,0,0],[0,0,0,0]]
    Y_noktaları = [[0,y,y,0],[0,y,y,0],[0,y,y,0],[0,0,y,y]]
    Z_noktaları = [[0,0,0,0],[0,0,z,z],[z,z,z,z],[0,z,z,0]]

    area_koordinat  = [X_noktaları,Y_noktaları,Z_noktaları]
    return area_koordinat



