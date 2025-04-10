
predefined_categories = {   "Tech":"https://i.pinimg.com/736x/c0/7e/af/c07eaf100ee852e4d1ec00704ab779da.jpg",
                            "Science":"https://i.pinimg.com/736x/5b/bc/8c/5bbc8cc4b2ffde0a0e9c528ca3f78f44.jpg",
                            "Health":"https://i.pinimg.com/736x/5c/f3/13/5cf3131eeb561b347f53a7c8a11bddf4.jpg", 
                            "Business":"https://i.pinimg.com/736x/4f/2a/0c/4f2a0c567410d325b893b46039859bbb.jpg", 
                            "Politics":"https://i.pinimg.com/736x/5f/15/a4/5f15a47e60f81da15d851c0af72a2cd1.jpg", 
                            "Entertainment":"https://i.pinimg.com/736x/af/b9/6b/afb96b38ea4e4c2295f9dcbc7760d1e6.jpg", 
                            "Sports":"https://i.pinimg.com/736x/8f/77/ae/8f77ae6e286fc4d47c54eeac6a9fbe91.jpg", 
                            "Education":"https://i.pinimg.com/736x/95/94/0e/95940eaece2b10fa9294a508ad3244a4.jpg", 
                            "Travel":"https://i.pinimg.com/736x/31/81/72/318172ee3135e9d347f857d9b3471c44.jpg", 
                            "Food":"https://i.pinimg.com/736x/02/de/6f/02de6fc2498da301942bbc72151afa5a.jpg", 
                            "Lifestyle":"https://i.pinimg.com/736x/ab/f9/bf/abf9bf25238e58abe3b20e7964780c32.jpg", 
                            "Fashion":"https://i.pinimg.com/736x/26/48/57/264857e17225e1d4b39f3fbdb83144ca.jpg", 
                            "Music":"https://i.pinimg.com/736x/3d/f6/b3/3df6b3bc7afcceeccd93b0dd801e187d.jpg", 
                            "Movies":"https://i.pinimg.com/736x/f9/08/28/f908289dac38614a11993725886d1be5.jpg", 
                            "Gaming":"https://i.pinimg.com/736x/3e/07/38/3e07385da605361404c266500ec5a33c.jpg", 
                            "News":"https://i.pinimg.com/736x/43/b9/ee/43b9ee0ac6fddd86eac1a9febbafce54.jpg", 
                            "Environment":"https://i.pinimg.com/736x/ae/c1/1e/aec11e1f72ccde26ec890f012e3df775.jpg", 
                            "Social Media":"https://i.pinimg.com/736x/0a/6a/c4/0a6ac40d1485b3a6e650d86be7c02c06.jpg", 
                            "Finance":"https://i.pinimg.com/736x/01/1a/1d/011a1d8e487f34f389a57a4eab6cd3b8.jpg", 
                            "Art":"https://i.pinimg.com/736x/d2/7f/ba/d27fba425b7544eef4a825c565deba42.jpg",
                            "Misc":"https://i.pinimg.com/736x/f6/29/e3/f629e354c589c15badcd6c323243e466.jpg"
                        }

def get_thumbnail(category: str):
    return predefined_categories.get(category)
