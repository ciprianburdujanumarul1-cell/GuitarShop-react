// Static catalog config — mirrors the brand cards that used to be hardcoded
// in electric.html / acoustic.html / bass.html.

export const CATEGORIES = {
  electric: {
    label: 'Electric',
    heroTitle: 'Electric',
    heroImage: 'https://images.unsplash.com/photo-1511379938547-c1f69419868d',
    brands: [
      {
        slug: 'esp',
        name: 'ESP LTD',
        image: 'https://cdn.connectsites.net/user_files/esp/articles/002/014/603/original.jpg?1609774690',
        desc: 'Aggressive build, tight low-end. Built for the heavy stuff.',
      },
      {
        slug: 'ibanez',
        name: 'Ibanez RG',
        image: 'https://guitar.com/wp-content/uploads/2020/07/Steve-Vai-Credit-C-Flanigan-FilmMagic@1400x1050-1068x801.jpg',
        desc: "Fast neck, versatile tone. The shredder's weapon of choice.",
      },
      {
        slug: 'fender',
        name: 'Fender Stratocaster',
        image: 'https://nafiriguitar.com/cdn/shop/files/947FB7C5-3F30-4C0D-A021-E9B2069D3254.jpg?v=1739517868&width=1946',
        desc: 'Timeless. Balanced pickups and iconic single-coil cut.',
      },
      {
        slug: 'jackson',
        name: 'Jackson',
        image: 'https://thumbs.static-thomann.de/thumb/padthumb600x600/pics/bdb/_46/463389/14626408_800.jpg',
        desc: 'Born in the 80s. Still drawing blood on modern stages.',
      },
      {
        slug: 'solar',
        name: 'Solar',
        image: 'https://i.ytimg.com/vi/TWoYRS5wqeY/hq720.jpg',
        desc: 'Swedish engineering meets modern extended-range fury.',
      },
      {
        slug: 'cort',
        name: 'Cort',
        image: 'https://thumbs.static-thomann.de/thumb/padthumb600x600/pics/bdb/_58/586632/19885614_800.jpg',
        desc: 'Serious performance at an honest price. No compromises.',
      },
    ],
  },
  acoustic: {
    label: 'Acoustic',
    heroTitle: 'Acoustic',
    heroImage: 'https://images.unsplash.com/photo-1511379938547-c1f69419868d',
    brands: [
      {
        slug: 'yamaha_acoustic',
        name: 'Yamaha Acoustic',
        image: 'https://guitarfactory.net/cdn/shop/collections/Menu-Guitars-Acoustic-004.jpg',
        desc: 'Warm tone, perfect for beginners & pros.',
      },
      {
        slug: 'fender_acoustic',
        name: 'Fender Acoustic',
        image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRY8365Bj3pmAjXp3tHbtZ_Tkfoqb22fx2Ua3HDqO0raP2zQkXTurJxUURb&s=10',
        desc: 'Classic look with rich resonance.',
      },
      {
        slug: 'ibanez_acoustic',
        name: 'Ibanez Acoustic',
        image: 'https://www.ibanez.com/common/product_artist_file/file/pc_main_acoustic_guitars_na_sp.jpg',
        desc: 'Slim neck, modern feel.',
      },
    ],
  },
  bass: {
    label: 'Bass',
    heroTitle: 'Bass',
    heroImage: 'https://images.unsplash.com/photo-1511379938547-c1f69419868d',
    brands: [
      {
        slug: 'yamaha_bass',
        name: 'Yamaha Bass',
        image: 'https://www.normans.co.uk/cdn/shop/products/B097HR1LDT.PT05_800x.jpg',
        desc: 'Solid low-end with great clarity.',
      },
      {
        slug: 'ibanez_bass',
        name: 'Ibanez Bass',
        image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSPUC-kFKUJNGFGaptz5Ho7of66vPqP1YhCA7HCy26wUQ&s',
        desc: 'Fast neck and modern tone.',
      },
      {
        slug: 'fender_bass',
        name: 'Fender Jazz Bass',
        image: 'https://mississaugafineartsacademy.com/wp-content/uploads/2021/02/How-to-Tune-Bass-Guitar-Video.jpg',
        desc: 'Classic tone used in countless records.',
      },
    ],
  },
}
