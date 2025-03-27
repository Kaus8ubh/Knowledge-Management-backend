import random

thumbnails = {
    "img1": "https://s46675.pcdn.co/wp-content/uploads/2009/12/abstract-photography-29.jpg",
    "img2": "https://s46675.pcdn.co/wp-content/uploads/2009/12/abstract-photography-25.jpg",
    "img3": "https://s46675.pcdn.co/wp-content/uploads/2019/01/abstractphoto11.jpg",
    "img4": "https://s46675.pcdn.co/wp-content/uploads/2009/12/abstract-photography-4.jpg",
    "img5": "https://s46675.pcdn.co/wp-content/uploads/2009/12/abstract-photography-29.jpg",
    "img6": "https://s46675.pcdn.co/wp-content/uploads/2019/01/abstractphoto16.jpg",
    "img7": "https://s46675.pcdn.co/wp-content/uploads/2009/12/abstract-photography-7.jpg",
    "img8": "https://s46675.pcdn.co/wp-content/uploads/2019/01/abstractphoto13.jpg",
    "img9": "https://s46675.pcdn.co/wp-content/uploads/2009/12/abstract-photography-10.jpg",
    "img10": "https://s46675.pcdn.co/wp-content/uploads/2019/01/abstractpic01.jpg",
    "img11": "https://s46675.pcdn.co/wp-content/uploads/2009/12/abstract-photography-39.jpg",
    "img12": "https://s46675.pcdn.co/wp-content/uploads/2009/12/abstract-photography-40.jpg"
}

def get_thumbnail():
    return random.choice(list(thumbnails.values()))

