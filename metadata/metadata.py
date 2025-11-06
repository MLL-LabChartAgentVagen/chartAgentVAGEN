"""
MetaData
"""

META_CATEGORIES = [
    "1 - Media & Entertainment",
    "2 - Geography & Demography",
    "3 - Education & Academia",
    "4 - Business & Industry",
    "5 - Major & Course",
    "6 - Animal & Zoology",
    "7 - Plant & Botany",
    "8 - Biology & Chemistry",
    "9 - Food & Nutrition",
    "10 - Space & Astronomy",
    "11 - Sale & Merchandise",
    "12 - Market & Economy",
    "13 - Sports & Athletics",
    "14 - Computing & Technology",
    "15 - Health & Medicine",
    "16 - Energy & Environment",
    "17 - Travel & Expedition",
    "18 - Arts & Culture",
    "19 - Communication & Collaboration",
    "20 - Language & Linguistics",
    "21 - History & Archaeology",
    "22 - Weather & Climate",
    "23 - Transportation & Infrastructure",
    "24 - Psychology & Personality",
    "25 - Materials & Engineering",
    "26 - Philanthropy & Charity",
    "27 - Fashion & Apparel",
    "28 - Parenting & Child Development",
    "29 - Architecture & Urban Planning",
    "30 - Gaming & Recreation", 
]

METADATA_DEMO = {
    "draw__1_bar__func_1": {
        "1 - Media & Entertainment": [],
        "2 - Geography & Demography": [],
        "3 - Education & Academia": [],
        "4 - Business & Industry": [],
        "5 - Major & Course": [],
        "6 - Animal & Zoology": [],
        "7 - Plant & Botany": [],
        "8 - Biology & Chemistry": [],
        "9 - Food & Nutrition": [],
        "10 - Space & Astronomy": [],
        "11 - Sale & Merchandise": [],
        "12 - Market & Economy": [],
        "13 - Sports & Athletics": [],
        "14 - Computing & Technology": [],
        "15 - Health & Medicine": [],
        "16 - Energy & Environment": [],
        "17 - Travel & Expedition": [],
        "18 - Arts & Culture": [],
        "19 - Communication & Collaboration": [],
        "20 - Language & Linguistics": [],
        "21 - History & Archaeology": [],
        "22 - Weather & Climate": [],
        "23 - Transportation & Infrastructure": [],
        "24 - Psychology & Personality": [],
        "25 - Materials & Engineering": [],
        "26 - Philanthropy & Charity": [],
        "27 - Fashion & Apparel": [],
        "28 - Parenting & Child Development": [],
        "29 - Architecture & Urban Planning": [],
        "30 - Gaming & Recreation": [], 
    }
}

METADATA_BAR = {
    "draw__1_bar__func_1": {
        "1 - Media & Entertainment": [
            {
                "bar_data": [22.75, 32.43, 33.96, 45.36, 19.32, 38.64, 55.72, 58.91, 40.11, 27.84],
                "bar_labels": ["Inception", "The Grand Budapest Hotel", "The Matrix", "Spirited Away", "Parasite", "Pulp Fiction", "The Dark Knight", "Titanic", "Interstellar", "The Shawshank Redemption"],
                "bar_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4"],
                "y_label": "Annual Box Office Earnings ($ Million)",
                "x_label": "Movies",
                "img_title": "Top 10 Movies: Annual Box Office Earnings",
            },
            {
                "bar_data": [1250.43, 986.32, 1354.87, 1789.65, 843.21, 2104.57, 1643.25, 756.91, 1492.36, 1028.74],
                "bar_labels": ["Netflix", "Disney+", "HBO Max", "Amazon Prime", "Hulu", "YouTube Premium", "Apple TV+", "Paramount+", "Peacock", "Crunchyroll"],
                "bar_colors": ["#E50914", "#0063E5", "#5822B4", "#00A8E1", "#1CE783", "#FF0000", "#2279E4", "#0064FF", "#C02222", "#F47521"],
                "y_label": "Subscribers (Millions)",
                "x_label": "Streaming Services",
                "img_title": "Global Subscriber Count by Streaming Service",
            },
            {
                "bar_data": [187.65, 154.23, 142.89, 205.47, 178.36, 163.92, 149.58, 191.27, 138.45, 172.81],
                "bar_labels": ["Action", "Comedy", "Drama", "Science Fiction", "Horror", "Fantasy", "Romance", "Adventure", "Mystery", "Animation"],
                "bar_colors": ["#D04848", "#F3B95F", "#6895D2", "#3E54AC", "#1A1A1A", "#C539B4", "#F25287", "#5D9C59", "#332941", "#FFC93C"],
                "y_label": "Average Revenue ($ Million)",
                "x_label": "Film Genres",
                "img_title": "Average Box Office Revenue by Film Genre",
            },
            {
                "bar_data": [42.3, 38.7, 29.1, 34.5, 45.8, 27.6, 36.2, 31.9, 40.3, 33.8],
                "bar_labels": ["Game of Thrones", "Breaking Bad", "The Office", "Friends", "Stranger Things", "The Crown", "The Mandalorian", "The Simpsons", "The Walking Dead", "The Witcher"],
                "bar_colors": ["#2E282A", "#17BEBB", "#CD5334", "#EDB88B", "#FAD8D6", "#CEB5A7", "#839788", "#FFDF64", "#A2A77F", "#D8973C"],
                "y_label": "Average Viewership per Episode (Millions)",
                "x_label": "TV Shows",
                "img_title": "Most Watched TV Shows of the Decade",
            },
            {
                "bar_data": [135.8, 98.4, 112.7, 142.3, 87.6, 104.9, 127.5, 93.2, 118.6, 131.4],
                "bar_labels": ["Social Media", "Video Games", "TV Shows", "Movies", "Books", "Music", "Video Content", "News", "Podcasts", "Sports"],
                "bar_colors": ["#3B5998", "#7B2CBF", "#FF5700", "#E50914", "#5D8AA8", "#1DB954", "#FF0000", "#071D49", "#8940FA", "#E90052"],
                "y_label": "Average Weekly Consumption (Minutes)",
                "x_label": "Entertainment Categories",
                "img_title": "Weekly Media Consumption by Category",
            },
            {
                "bar_data": [8.7, 7.9, 8.3, 9.1, 7.5, 8.9, 7.8, 8.2, 9.3, 8.5],
                "bar_labels": ["Beyoncé", "Taylor Swift", "Drake", "BTS", "Ariana Grande", "The Weeknd", "Billie Eilish", "Ed Sheeran", "Bad Bunny", "Justin Bieber"],
                "bar_colors": ["#F4B400", "#7B5576", "#2E2E46", "#8D8FD9", "#A7D7C5", "#3B3F42", "#539AAC", "#BC5D2E", "#FE0000", "#9B26B6"],
                "y_label": "Monthly Listeners (Millions)",
                "x_label": "Artists",
                "img_title": "Top Musicians by Monthly Listeners",
            },
            {
                "bar_data": [145.3, 128.7, 137.9, 152.6, 119.8, 133.4, 141.5, 126.2, 148.9, 130.1],
                "bar_labels": ["Disney", "Warner Bros", "Universal", "Sony Pictures", "Paramount", "20th Century Studios", "Lionsgate", "Netflix Studios", "A24", "DreamWorks"],
                "bar_colors": ["#0070D1", "#066DC5", "#2F22AB", "#F47521", "#0057B8", "#0061D2", "#E4202E", "#E50914", "#00A36C", "#98C0D9"],
                "y_label": "Annual Revenue ($ Billion)",
                "x_label": "Studios",
                "img_title": "Top Film Studios by Annual Revenue",
            },
            {
                "bar_data": [12.4, 9.7, 11.3, 8.5, 10.2, 7.8, 9.9, 11.6, 8.1, 10.8],
                "bar_labels": ["Call of Duty", "Minecraft", "Grand Theft Auto", "FIFA", "Fortnite", "League of Legends", "Roblox", "Apex Legends", "Valorant", "The Sims"],
                "bar_colors": ["#0A0A0A", "#78BE20", "#0252F8", "#326295", "#9D4DFF", "#3CBCEB", "#F54747", "#CC0000", "#FF4655", "#3C8C79"],
                "y_label": "Annual Player Base (Millions)",
                "x_label": "Video Games",
                "img_title": "Most Popular Video Games by Player Count",
            },
            {
                "bar_data": [65.2, 59.7, 71.4, 62.9, 58.3, 69.8, 60.5, 68.1, 57.6, 63.8],
                "bar_labels": ["Instagram", "YouTube", "TikTok", "Facebook", "Twitter", "Snapchat", "Reddit", "Pinterest", "LinkedIn", "Twitch"],
                "bar_colors": ["#E1306C", "#FF0000", "#000000", "#4267B2", "#1DA1F2", "#FFFC00", "#FF4500", "#E60023", "#0077B5", "#9146FF"],
                "y_label": "Daily Active Users (Millions)",
                "x_label": "Social Media Platforms",
                "img_title": "Social Media Popularity by Active Users",
            },
            {
                "bar_data": [3.1, 2.8, 3.5, 2.7, 3.9, 3.2, 2.9, 3.7, 3.0, 3.4],
                "bar_labels": ["Celebrity News", "Movie Reviews", "Music Releases", "TV Show Recaps", "Gaming Updates", "Award Shows", "Concert Tours", "Streaming Releases", "Book Launches", "Fan Conventions"],
                "bar_colors": ["#FF8500", "#8C52FF", "#FF4242", "#3B806C", "#7C73E6", "#FEBC38", "#E8486A", "#82CAA9", "#574F9A", "#FFEE99"],
                "y_label": "Average Weekly Engagement (Hours)",
                "x_label": "Entertainment News Categories",
                "img_title": "Entertainment News Consumption by Category",
            },
        ],
        "2 - Geography & Demography": [
            {
                "bar_data": [1439.3, 1380.0, 331.0, 273.5, 220.9, 212.6, 201.1, 164.7, 147.6, 126.5],
                "bar_labels": ["China", "India", "United States", "Indonesia", "Pakistan", "Brazil", "Nigeria", "Bangladesh", "Russia", "Mexico"],
                "bar_colors": ["#DE2910", "#FF9933", "#3C3B6E", "#FF0000", "#01411C", "#009C3B", "#008751", "#006A4E", "#0039A6", "#006847"],
                "y_label": "Population (Millions)",
                "x_label": "Countries",
                "img_title": "World's Most Populous Countries",
            },
            {
                "bar_data": [28.52, 17.84, 15.29, 12.38, 9.76, 8.51, 7.63, 6.92, 5.48, 4.27],
                "bar_labels": ["Tokyo", "Delhi", "Shanghai", "São Paulo", "Mexico City", "Cairo", "Mumbai", "Beijing", "Dhaka", "Osaka"],
                "bar_colors": ["#BC002D", "#FF9933", "#DE2910", "#009C3B", "#006847", "#C8102E", "#FF9933", "#DE2910", "#006A4E", "#BC002D"],
                "y_label": "Population (Millions)",
                "x_label": "Cities",
                "img_title": "World's Most Populous Urban Areas",
            },
            {
                "bar_data": [83.87, 82.75, 84.93, 81.32, 83.78, 85.21, 80.96, 84.36, 82.46, 83.14],
                "bar_labels": ["Japan", "Switzerland", "Hong Kong", "Australia", "Norway", "Singapore", "Italy", "Iceland", "South Korea", "Sweden"],
                "bar_colors": ["#BC002D", "#FF0000", "#DE2910", "#00008B", "#FF0000", "#EF2B2D", "#009246", "#003897", "#0047A0", "#FECC02"],
                "y_label": "Life Expectancy (Years)",
                "x_label": "Countries",
                "img_title": "Countries with Highest Life Expectancy",
            },
            {
                "bar_data": [17.10, 9.83, 9.15, 8.51, 6.69, 5.97, 3.29, 3.05, 2.72, 2.68],
                "bar_labels": ["Russia", "Canada", "United States", "China", "Brazil", "Australia", "India", "Argentina", "Kazakhstan", "Algeria"],
                "bar_colors": ["#0039A6", "#FF0000", "#3C3B6E", "#DE2910", "#009C3B", "#00008B", "#FF9933", "#75AADB", "#00AFCA", "#006233"],
                "y_label": "Land Area (Million km²)",
                "x_label": "Countries",
                "img_title": "World's Largest Countries by Land Area",
            },
            {
                "bar_data": [42.95, 38.21, 36.74, 33.89, 31.57, 29.83, 27.62, 25.94, 24.18, 22.73],
                "bar_labels": ["Niger", "Angola", "Mali", "Somalia", "Congo", "Burkina Faso", "Uganda", "Nigeria", "Gambia", "Mozambique"],
                "bar_colors": ["#E05206", "#CE1126", "#14B53A", "#4189DD", "#007FFF", "#009E49", "#FCDC04", "#008751", "#3A7728", "#009639"],
                "y_label": "Median Age (Years)",
                "x_label": "Countries",
                "img_title": "Countries with Youngest Populations",
            },
            {
                "bar_data": [27.68, 24.95, 22.13, 19.86, 16.52, 14.78, 12.34, 10.97, 9.65, 8.49],
                "bar_labels": ["United States", "China", "Japan", "Germany", "United Kingdom", "India", "France", "Italy", "Canada", "South Korea"],
                "bar_colors": ["#3C3B6E", "#DE2910", "#BC002D", "#000000", "#00247D", "#FF9933", "#002395", "#009246", "#FF0000", "#0047A0"],
                "y_label": "GDP (Trillion $)",
                "x_label": "Countries",
                "img_title": "Countries with Highest GDP",
            },
            {
                "bar_data": [37.21, 34.68, 32.95, 30.47, 28.76, 26.53, 24.89, 22.34, 20.18, 18.57],
                "bar_labels": ["Manhattan", "San Francisco", "London", "Sydney", "Singapore", "Hong Kong", "Los Angeles", "Paris", "Tokyo", "Geneva"],
                "bar_colors": ["#313131", "#E4002B", "#E32636", "#002B7F", "#EF2B2D", "#DE2910", "#FFB300", "#002395", "#BC002D", "#FF0000"],
                "y_label": "Average Monthly Rent (Hundred $)",
                "x_label": "Cities",
                "img_title": "World's Most Expensive Cities to Rent",
            },
            {
                "bar_data": [196.5, 178.2, 162.7, 149.3, 135.8, 122.4, 114.9, 106.3, 97.8, 85.2],
                "bar_labels": ["Mediterranean", "East Asia", "Northern Europe", "South Asia", "Latin America", "Eastern Europe", "Middle East", "Southeast Asia", "North America", "Sub-Saharan Africa"],
                "bar_colors": ["#7EAED9", "#DE2910", "#005B99", "#FF9933", "#7AC143", "#0039A6", "#C09300", "#EE334E", "#3B7CC0", "#008751"],
                "y_label": "Population Density (per km²)",
                "x_label": "Regions",
                "img_title": "Population Density by World Region",
            },
            {
                "bar_data": [19.63, 18.45, 17.92, 16.78, 15.34, 14.29, 13.81, 12.96, 11.57, 10.83],
                "bar_labels": ["Christianity", "Islam", "Hinduism", "Buddhism", "Folk Religions", "Atheism/Agnosticism", "Judaism", "Sikhism", "Shinto", "Taoism"],
                "bar_colors": ["#7575CF", "#009E49", "#FF9933", "#FFCC00", "#CD7F32", "#A9A9A9", "#0038B8", "#0D698B", "#C73500", "#C41E3A"],
                "y_label": "Global Adherents (%)",
                "x_label": "Religions",
                "img_title": "World Religious Demographics",
            },
            {
                "bar_data": [4.78, 3.96, 3.57, 3.28, 2.95, 2.74, 2.46, 2.31, 2.09, 1.87],
                "bar_labels": ["English", "Mandarin", "Hindi", "Spanish", "French", "Arabic", "Bengali", "Russian", "Portuguese", "Indonesian"],
                "bar_colors": ["#CF142B", "#DE2910", "#FF9933", "#FCDD09", "#002395", "#078930", "#006A4E", "#0039A6", "#006600", "#FF0000"],
                "y_label": "Speakers (Billions)",
                "x_label": "Languages",
                "img_title": "World's Most Spoken Languages",
            },
        ],
        "3 - Education & Academia": [
            {
                "bar_data": [95.7, 93.2, 91.8, 90.4, 89.1, 87.6, 86.3, 84.9, 83.5, 82.1],
                "bar_labels": ["Massachusetts", "Maryland", "Connecticut", "New Jersey", "Vermont", "New Hampshire", "Virginia", "Minnesota", "Colorado", "Washington"],
                "bar_colors": ["#B31942", "#6699CC", "#00853E", "#D8B93B", "#1D7F3D", "#8D1D2C", "#0052A5", "#1A1557", "#002868", "#00ADA7"],
                "y_label": "High School Graduation Rate (%)",
                "x_label": "States",
                "img_title": "High School Graduation Rates by State",
            },
            {
                "bar_data": [9.87, 9.42, 9.15, 8.97, 8.81, 8.63, 8.29, 8.14, 7.96, 7.73],
                "bar_labels": ["Harvard", "MIT", "Stanford", "Oxford", "Cambridge", "Caltech", "Princeton", "Yale", "UC Berkeley", "Columbia"],
                "bar_colors": ["#A51C30", "#8A8B8C", "#8C1515", "#002147", "#A3C1AD", "#FF6C0C", "#F58025", "#00356B", "#003262", "#0032A0"],
                "y_label": "Annual Research Output (Thousands of Papers)",
                "x_label": "Universities",
                "img_title": "Top Universities by Research Publication",
            },
            {
                "bar_data": [86.5, 79.2, 74.8, 70.3, 67.9, 64.2, 61.7, 58.9, 55.4, 52.1],
                "bar_labels": ["Finland", "Denmark", "Japan", "South Korea", "Netherlands", "Canada", "Germany", "Australia", "United Kingdom", "United States"],
                "bar_colors": ["#002F6C", "#C60C30", "#BC002D", "#0047A0", "#AE1C28", "#FF0000", "#000000", "#00008B", "#CF142B", "#3C3B6E"],
                "y_label": "Education System Ranking Score",
                "x_label": "Countries",
                "img_title": "Global Education System Quality Rankings",
            },
            {
                "bar_data": [42.3, 38.7, 35.1, 32.6, 30.8, 28.4, 26.9, 24.3, 22.1, 19.8],
                "bar_labels": ["Computer Science", "Business Admin", "Engineering", "Nursing", "Psychology", "Biology", "Education", "Communications", "Economics", "Political Science"],
                "bar_colors": ["#4285F4", "#F4B400", "#0F9D58", "#4285F4", "#AA336A", "#2E8B57", "#1E90FF", "#FF8C00", "#006400", "#800000"],
                "y_label": "Enrollment (Thousands)",
                "x_label": "College Majors",
                "img_title": "Most Popular College Majors by Enrollment",
            },
            {
                "bar_data": [9.47, 8.56, 7.82, 6.93, 6.29, 5.74, 5.18, 4.65, 4.21, 3.87],
                "bar_labels": ["South Korea", "Finland", "Israel", "Japan", "Singapore", "Sweden", "United States", "Germany", "Australia", "United Kingdom"],
                "bar_colors": ["#0047A0", "#002F6C", "#0038B8", "#BC002D", "#EF3340", "#FECC02", "#3C3B6E", "#000000", "#00008B", "#CF142B"],
                "y_label": "Education Spending (% of GDP)",
                "x_label": "Countries",
                "img_title": "Countries' Investment in Education",
            },
            {
                "bar_data": [156.8, 142.3, 127.5, 114.9, 103.2, 92.7, 83.5, 75.1, 67.8, 61.4],
                "bar_labels": ["Private University", "Public Out-of-State", "Private Liberal Arts", "Public In-State", "Community College", "Technical Institute", "Online University", "Trade School", "Apprenticeship", "Certificate Program"],
                "bar_colors": ["#800000", "#4B2E83", "#00356B", "#7A0019", "#00B5E2", "#E87722", "#003262", "#8B2332", "#D4AF37", "#006747"],
                "y_label": "Average Annual Cost (Hundred $)",
                "x_label": "Education Types",
                "img_title": "Cost Comparison of Education Paths",
            },
            {
                "bar_data": [42.8, 37.5, 34.2, 31.9, 29.6, 27.3, 25.1, 22.8, 20.5, 18.7],
                "bar_labels": ["Science", "Health Sciences", "Engineering", "Mathematics", "Computer Sciences", "Social Sciences", "Humanities", "Business", "Education", "Arts"],
                "bar_colors": ["#4D4DFF", "#FF6B6B", "#FFA500", "#32CD32", "#9370DB", "#FFD700", "#8B4513", "#00CED1", "#FF69B4", "#2F4F4F"],
                "y_label": "Citation Impact Score",
                "x_label": "Academic Fields",
                "img_title": "Citation Impact by Academic Discipline",
            },
            {
                "bar_data": [86.3, 82.7, 79.4, 75.8, 72.1, 68.5, 65.2, 61.9, 58.4, 55.1],
                "bar_labels": ["Pediatricians", "Engineers", "Computer Scientists", "Dentists", "Pharmacists", "Physicians", "Nurse Practitioners", "Physical Therapists", "Accountants", "Teachers"],
                "bar_colors": ["#FF4500", "#1E90FF", "#32CD32", "#FFD700", "#9370DB", "#FF6347", "#4682B4", "#8FBC8F", "#DAA520", "#BA55D3"],
                "y_label": "Job Placement Rate (%)",
                "x_label": "Professional Fields",
                "img_title": "Job Placement Rates by Professional Field",
            },
            {
                "bar_data": [9.73, 8.95, 8.27, 7.64, 7.18, 6.89, 6.42, 5.93, 5.51, 5.16],
                "bar_labels": ["Bill & Melinda Gates", "Ford Foundation", "Carnegie Foundation", "MacArthur Foundation", "Rockefeller Foundation", "Chan Zuckerberg Initiative", "Walton Family Foundation", "Howard Hughes Medical Institute", "Andrew W. Mellon Foundation", "William and Flora Hewlett Foundation"],
                "bar_colors": ["#F25022", "#00539B", "#B83A4B", "#003591", "#0067A0", "#4267B2", "#00205B", "#0033A0", "#006BA6", "#C41230"],
                "y_label": "Annual Funding ($ Billion)",
                "x_label": "Foundations",
                "img_title": "Major Education Grant Funding Sources",
            },
            {
                "bar_data": [94.7, 92.5, 89.6, 86.3, 83.8, 80.2, 77.9, 74.5, 71.3, 68.1],
                "bar_labels": ["Software Engineering", "Computer Science", "Nursing", "Electrical Engineering", "Petroleum Engineering", "Finance", "Cybersecurity", "Data Science", "Aerospace Engineering", "Economics"],
                "bar_colors": ["#5F9EA0", "#00008B", "#4B0082", "#8B0000", "#2F4F4F", "#BDB76B", "#8B4513", "#6495ED", "#4169E1", "#008080"],
                "y_label": "Early Career Employment Rate (%)",
                "x_label": "College Majors",
                "img_title": "Employment Rates by College Major",
            },
        ],
        "4 - Business & Industry": [
            {
                "bar_data": [2850.37, 2415.82, 1976.54, 1843.29, 1692.84, 1485.63, 1354.92, 1227.38, 1105.49, 987.65],
                "bar_labels": ["Apple", "Microsoft", "Saudi Aramco", "Alphabet", "Amazon", "NVIDIA", "Meta", "Berkshire Hathaway", "Tesla", "TSMC"],
                "bar_colors": ["#A2AAAD", "#00A4EF", "#005F61", "#4285F4", "#FF9900", "#76B900", "#1877F2", "#0038B8", "#CC0000", "#0076CE"],
                "y_label": "Market Capitalization ($ Billion)",
                "x_label": "Companies",
                "img_title": "Top 10 Companies by Market Capitalization",
            },
            {
                "bar_data": [467.15, 386.29, 315.42, 294.87, 263.74, 235.19, 208.63, 187.45, 159.37, 128.92],
                "bar_labels": ["Retail", "Healthcare", "Technology", "Financial Services", "Manufacturing", "Energy", "Real Estate", "Telecommunications", "Transportation", "Agriculture"],
                "bar_colors": ["#FF9900", "#0072CE", "#4285F4", "#117864", "#C0392B", "#F39C12", "#8E44AD", "#3498DB", "#D35400", "#1E8449"],
                "y_label": "Global Revenue ($ Trillion)",
                "x_label": "Industries",
                "img_title": "Global Industry Revenue Distribution",
            },
            {
                "bar_data": [42.3, 38.7, 35.2, 32.9, 29.5, 26.8, 24.1, 21.6, 19.4, 17.8],
                "bar_labels": ["Software Development", "Healthcare", "Renewable Energy", "E-commerce", "Cybersecurity", "Artificial Intelligence", "Biotechnology", "Digital Marketing", "Financial Technology", "Remote Work Solutions"],
                "bar_colors": ["#8D6E63", "#4FC3F7", "#66BB6A", "#FF7043", "#5C6BC0", "#42A5F5", "#EC407A", "#AB47BC", "#26A69A", "#FFA726"],
                "y_label": "Annual Growth Rate (%)",
                "x_label": "Business Sectors",
                "img_title": "Fastest Growing Business Sectors",
            },
            {
                "bar_data": [15.37, 14.25, 13.68, 12.94, 11.82, 10.59, 9.73, 8.48, 7.36, 6.21],
                "bar_labels": ["Alibaba", "Amazon", "eBay", "Rakuten", "Walmart", "JD.com", "MercadoLibre", "Coupang", "Shopify", "Etsy"],
                "bar_colors": ["#FF7300", "#FF9900", "#85B716", "#BF0000", "#004C91", "#D71C06", "#FFE600", "#5B2D82", "#96BF48", "#F56400"],
                "y_label": "Annual E-commerce Revenue ($ Billion)",
                "x_label": "Companies",
                "img_title": "Leading E-commerce Platforms by Revenue",
            },
            {
                "bar_data": [87.6, 82.3, 79.8, 76.4, 73.9, 71.2, 68.7, 65.3, 62.8, 59.5],
                "bar_labels": ["Japan", "Germany", "South Korea", "Switzerland", "Sweden", "Denmark", "Netherlands", "United States", "United Kingdom", "Singapore"],
                "bar_colors": ["#BC002D", "#000000", "#0047A0", "#FF0000", "#FECC02", "#C60C30", "#AE1C28", "#3C3B6E", "#CF142B", "#EF3340"],
                "y_label": "Manufacturing Efficiency Index",
                "x_label": "Countries",
                "img_title": "Global Manufacturing Efficiency by Country",
            },
            {
                "bar_data": [156.7, 143.2, 132.5, 124.8, 117.6, 108.3, 96.9, 88.4, 79.2, 73.5],
                "bar_labels": ["Financial Services", "Information Technology", "Healthcare", "Energy", "Consumer Discretionary", "Communication Services", "Industrials", "Consumer Staples", "Materials", "Utilities"],
                "bar_colors": ["#043927", "#0071C5", "#3F51B5", "#FF9800", "#F44336", "#9C27B0", "#795548", "#8BC34A", "#607D8B", "#FFC107"],
                "y_label": "Average CEO Compensation ($ Hundred Thousand)",
                "x_label": "Industry Sectors",
                "img_title": "CEO Compensation Across Industry Sectors",
            },
            {
                "bar_data": [32.8, 29.5, 27.3, 25.1, 23.7, 21.6, 19.4, 17.2, 15.9, 14.3],
                "bar_labels": ["Construction", "Manufacturing", "Transportation", "Warehousing", "Agriculture", "Mining", "Utilities", "Waste Management", "Fishing", "Forestry"],
                "bar_colors": ["#FFC300", "#C70039", "#900C3F", "#581845", "#DAF7A6", "#FFC300", "#FF5733", "#C70039", "#2471A3", "#28B463"],
                "y_label": "Workplace Injury Rate (per 1,000 workers)",
                "x_label": "Industries",
                "img_title": "Workplace Safety: Injury Rates by Industry",
            },
            {
                "bar_data": [43.2, 39.8, 36.5, 33.9, 31.2, 28.7, 26.3, 24.1, 21.8, 19.5],
                "bar_labels": ["Information Technology", "Healthcare", "Financial Services", "Professional Services", "Manufacturing", "Construction", "Retail", "Education", "Hospitality", "Transportation"],
                "bar_colors": ["#3498DB", "#E74C3C", "#2ECC71", "#F39C12", "#9B59B6", "#1ABC9C", "#D35400", "#34495E", "#7F8C8D", "#2980B9"],
                "y_label": "Employee Turnover Rate (%)",
                "x_label": "Industry Sectors",
                "img_title": "Employee Turnover Rates by Industry",
            },
            {
                "bar_data": [76.3, 72.8, 69.5, 67.1, 64.7, 62.3, 59.8, 57.4, 55.1, 52.8],
                "bar_labels": ["Technology", "Pharmaceutical", "Aerospace", "Automotive", "Chemical", "Energy", "Telecommunications", "Electronics", "Machinery", "Food Processing"],
                "bar_colors": ["#007BFF", "#6610F2", "#6F42C1", "#E83E8C", "#DC3545", "#FD7E14", "#FFC107", "#28A745", "#20C997", "#17A2B8"],
                "y_label": "R&D Investment ($ Billion)",
                "x_label": "Manufacturing Sectors",
                "img_title": "R&D Investment by Manufacturing Sector",
            },
            {
                "bar_data": [358.9, 324.6, 297.8, 273.5, 249.2, 226.7, 207.3, 189.6, 172.4, 158.9],
                "bar_labels": ["Alphabet", "Amazon", "Microsoft", "Meta", "Apple", "TSMC", "Samsung", "Johnson & Johnson", "Roche", "Volkswagen"],
                "bar_colors": ["#4285F4", "#FF9900", "#00A4EF", "#1877F2", "#A2AAAD", "#0076CE", "#1428A0", "#D80027", "#00205B", "#001E50"],
                "y_label": "Annual R&D Spending ($ Million)",
                "x_label": "Companies",
                "img_title": "Top 10 Companies by R&D Investment",
            },
        ],
        "5 - Major & Course": [
            {
                "bar_data": [78.6, 74.3, 71.8, 68.5, 65.2, 62.9, 59.7, 56.4, 53.2, 50.8],
                "bar_labels": ["Computer Science", "Nursing", "Business Administration", "Engineering", "Education", "Psychology", "Biology", "Communications", "Economics", "Political Science"],
                "bar_colors": ["#4285F4", "#EA4335", "#FBBC05", "#34A853", "#5C6BC0", "#AB47BC", "#26A69A", "#FFA726", "#EF5350", "#66BB6A"],
                "y_label": "Starting Salary ($ Thousand)",
                "x_label": "Majors",
                "img_title": "Average Starting Salaries by College Major",
            },
            {
                "bar_data": [45.3, 42.7, 38.9, 36.2, 33.8, 30.5, 27.9, 25.4, 22.8, 19.6],
                "bar_labels": ["Harvard", "Yale", "MIT", "Stanford", "Princeton", "Columbia", "UPenn", "Dartmouth", "Brown", "Cornell"],
                "bar_colors": ["#A41034", "#00356B", "#A31F34", "#8C1515", "#FF8F00", "#B9D9EB", "#011F5B", "#00693E", "#C00", "#B31B1B"],
                "y_label": "Average Class Size",
                "x_label": "Universities",
                "img_title": "Average Class Sizes at Ivy League Universities",
            },
            {
                "bar_data": [94.7, 92.3, 89.8, 87.5, 85.2, 82.9, 80.6, 78.4, 76.1, 73.8],
                "bar_labels": ["Medicine", "Law", "Pharmacy", "Engineering", "Computer Science", "Finance", "Nursing", "Architecture", "Education", "Fine Arts"],
                "bar_colors": ["#C41E3A", "#0C2340", "#006B54", "#E87722", "#0077C8", "#4B2E83", "#007934", "#BA0C2F", "#0033A0", "#A67C52"],
                "y_label": "Employment Rate (%)",
                "x_label": "Fields of Study",
                "img_title": "Post-Graduation Employment Rates by Field",
            },
            {
                "bar_data": [4.35, 4.27, 4.19, 4.12, 4.05, 3.98, 3.91, 3.84, 3.77, 3.70],
                "bar_labels": ["Chemical Engineering", "Physics", "Mathematics", "Computer Engineering", "Electrical Engineering", "Mechanical Engineering", "Biology", "Chemistry", "Finance", "Economics"],
                "bar_colors": ["#FF5722", "#9C27B0", "#673AB7", "#3F51B5", "#2196F3", "#00BCD4", "#009688", "#4CAF50", "#CDDC39", "#FFEB3B"],
                "y_label": "Average GPA",
                "x_label": "Majors",
                "img_title": "Average GPA by College Major",
            },
            {
                "bar_data": [178.5, 165.2, 153.9, 142.7, 131.8, 121.3, 112.6, 104.9, 97.3, 89.8],
                "bar_labels": ["Medical School", "Law School", "MBA Program", "Dental School", "Pharmacy School", "Veterinary School", "Engineering Graduate", "Data Science", "Computer Science", "Public Health"],
                "bar_colors": ["#3F51B5", "#F44336", "#4CAF50", "#9C27B0", "#FF9800", "#FFEB3B", "#795548", "#2196F3", "#009688", "#607D8B"],
                "y_label": "Annual Tuition ($ Thousand)",
                "x_label": "Graduate Programs",
                "img_title": "Average Annual Tuition for Graduate Programs",
            },
            {
                "bar_data": [65.3, 62.8, 59.5, 56.9, 54.2, 51.7, 49.3, 46.8, 44.5, 42.1],
                "bar_labels": ["STEM", "Business", "Health Sciences", "Social Sciences", "Liberal Arts", "Education", "Fine Arts", "Agriculture", "Communications", "Interdisciplinary"],
                "bar_colors": ["#4285F4", "#DB4437", "#F4B400", "#0F9D58", "#AB47BC", "#00ACC1", "#FF7043", "#9E9D24", "#5C6BC0", "#00897B"],
                "y_label": "Graduation Rate (%)",
                "x_label": "Degree Categories",
                "img_title": "Graduation Rates by Degree Category",
            },
            {
                "bar_data": [168.5, 152.7, 143.6, 135.9, 127.8, 119.2, 112.4, 105.8, 99.3, 92.7],
                "bar_labels": ["Machine Learning", "Data Science", "Cybersecurity", "Blockchain", "Artificial Intelligence", "Cloud Computing", "UX Design", "Digital Marketing", "Software Engineering", "Mobile Development"],
                "bar_colors": ["#3498DB", "#9B59B6", "#2ECC71", "#F1C40F", "#E74C3C", "#1ABC9C", "#F39C12", "#D35400", "#7F8C8D", "#34495E"],
                "y_label": "Hours to Proficiency",
                "x_label": "Technical Courses",
                "img_title": "Time to Proficiency for Technical Courses",
            },
            {
                "bar_data": [3.95, 3.87, 3.79, 3.72, 3.64, 3.57, 3.49, 3.42, 3.35, 3.28],
                "bar_labels": ["Biochemistry", "Mathematics", "Physics", "Computer Science", "Electrical Engineering", "Economics", "Psychology", "Political Science", "Business", "Communications"],
                "bar_colors": ["#8BC34A", "#FFC107", "#FF5722", "#03A9F4", "#673AB7", "#CDDC39", "#9C27B0", "#FF9800", "#4CAF50", "#009688"],
                "y_label": "Average SAT Score (Thousands)",
                "x_label": "College Majors",
                "img_title": "Average SAT Scores by Declared Major",
            },
            {
                "bar_data": [187.3, 175.6, 164.8, 155.2, 146.5, 138.7, 131.9, 124.3, 116.9, 110.4],
                "bar_labels": ["Online Learning", "Full-time Campus", "Evening/Weekend", "Hybrid Programs", "Co-op Programs", "Study Abroad", "Summer Intensive", "Professional Certificate", "Continuing Education", "Self-paced"],
                "bar_colors": ["#FF5252", "#FF4081", "#E040FB", "#7C4DFF", "#536DFE", "#448AFF", "#40C4FF", "#18FFFF", "#64FFDA", "#69F0AE"],
                "y_label": "Credit Hours per Year",
                "x_label": "Program Types",
                "img_title": "Annual Credit Hours by Program Type",
            },
            {
                "bar_data": [84.6, 81.3, 78.9, 76.2, 73.8, 71.5, 69.1, 66.7, 64.4, 62.0],
                "bar_labels": ["MIT", "Stanford", "UC Berkeley", "Carnegie Mellon", "Georgia Tech", "Caltech", "University of Illinois", "University of Michigan", "Cornell", "Princeton"],
                "bar_colors": ["#A31F34", "#8C1515", "#003262", "#C41230", "#B3A369", "#FF6C0C", "#13294B", "#FFCB05", "#B31B1B", "#F77F00"],
                "y_label": "Placement Rate (%)",
                "x_label": "Universities",
                "img_title": "CS Graduate Placement Rates by University",
            },
        ],
        "6 - Animal & Zoology": [
            {
                "bar_data": [96.5, 87.2, 79.8, 72.3, 65.1, 58.7, 52.4, 46.9, 41.5, 36.2],
                "bar_labels": ["Blue Whale", "Fin Whale", "Sperm Whale", "Right Whale", "Humpback Whale", "Bowhead Whale", "Minke Whale", "Gray Whale", "Orca", "Sei Whale"],
                "bar_colors": ["#0077BE", "#005F73", "#0A9396", "#94D2BD", "#E9D8A6", "#EE9B00", "#CA6702", "#BB3E03", "#AE2012", "#9B2226"],
                "y_label": "Average Length (feet)",
                "x_label": "Marine Species",
                "img_title": "Size Comparison of Whale Species",
            },
            {
                "bar_data": [70.2, 63.5, 57.8, 52.1, 46.9, 41.3, 36.7, 32.4, 28.6, 25.2],
                "bar_labels": ["African Elephant", "Asian Elephant", "White Rhinoceros", "Hippopotamus", "Giraffe", "Gaur", "American Bison", "Polar Bear", "Moose", "Gorilla"],
                "bar_colors": ["#E48400", "#A66D03", "#A0A0A0", "#7E6E73", "#FFD700", "#8B4513", "#6F4E37", "#FFFFFF", "#7F3F00", "#1E1E1E"],
                "y_label": "Weight (Hundred kg)",
                "x_label": "Land Mammals",
                "img_title": "Largest Land Mammals by Weight",
            },
            {
                "bar_data": [389.4, 352.7, 319.5, 284.8, 256.3, 231.9, 209.7, 189.5, 171.3, 155.2],
                "bar_labels": ["Peregrine Falcon", "Golden Eagle", "Spine-tailed Swift", "Frigatebird", "Spur-winged Goose", "Red-breasted Merganser", "Eurasian Hobby", "White-throated Needletail", "Common Swift", "Gyrfalcon"],
                "bar_colors": ["#2F4F4F", "#8B4513", "#D2691E", "#080808", "#BC8F8F", "#556B2F", "#A0522D", "#696969", "#778899", "#708090"],
                "y_label": "Maximum Speed (km/h)",
                "x_label": "Bird Species",
                "img_title": "World's Fastest Birds by Flight Speed",
            },
            {
                "bar_data": [183.0, 167.4, 152.8, 138.9, 126.5, 115.3, 105.7, 96.8, 88.5, 80.7],
                "bar_labels": ["African Elephant", "Bottlenose Dolphin", "Chimpanzee", "Orangutan", "Crow", "Pig", "Octopus", "Dog", "African Grey Parrot", "Squirrel"],
                "bar_colors": ["#E48400", "#00BFFF", "#8B4513", "#D2691E", "#000000", "#FFC0CB", "#1E90FF", "#A52A2A", "#808080", "#B8860B"],
                "y_label": "Intelligence Quotient Estimate",
                "x_label": "Animal Species",
                "img_title": "Comparative Intelligence of Animal Species",
            },
            {
                "bar_data": [285.7, 247.9, 213.6, 184.2, 158.5, 136.3, 117.9, 101.2, 87.4, 75.3],
                "bar_labels": ["Leatherback Turtle", "Green Turtle", "Galapagos Tortoise", "Aldabra Tortoise", "Loggerhead Turtle", "Radiated Tortoise", "Ornate Box Turtle", "Red-eared Slider", "Desert Tortoise", "Painted Turtle"],
                "bar_colors": ["#483C32", "#3B7A57", "#708238", "#65560D", "#B87333", "#FFF8DC", "#AA4A44", "#614B3A", "#BDB76B", "#20B2AA"],
                "y_label": "Lifespan (years)",
                "x_label": "Turtle/Tortoise Species",
                "img_title": "Longevity of Turtle and Tortoise Species",
            },
            {
                "bar_data": [4.7, 4.3, 3.9, 3.6, 3.2, 2.9, 2.6, 2.3, 2.0, 1.8],
                "bar_labels": ["Sailfish", "Marlin", "Swordfish", "Yellowfin Tuna", "Wahoo", "Bluefin Tuna", "Bonefish", "Dorado", "Tarpon", "Barracuda"],
                "bar_colors": ["#001F3F", "#3581D7", "#0B3954", "#FFDD00", "#4E8098", "#1A5276", "#85C1E9", "#73C2FB", "#7B9EA8", "#94B8B8"],
                "y_label": "Maximum Speed (m/s)",
                "x_label": "Fish Species",
                "img_title": "Fastest Fish Species in Ocean Waters",
            },
            {
                "bar_data": [37846.2, 35172.5, 32493.7, 30253.8, 27867.4, 25619.6, 23481.5, 21342.8, 19568.3, 17924.6],
                "bar_labels": ["Insects", "Crustaceans", "Mollusks", "Arachnids", "Fish", "Birds", "Reptiles", "Amphibians", "Mammals", "Echinoderms"],
                "bar_colors": ["#F49E42", "#5C8D89", "#FFC3A0", "#D8345F", "#9CD08F", "#A9C8C0", "#3D5A6C", "#82A7A6", "#E8871E", "#CDB3B0"],
                "y_label": "Number of Species (thousands)",
                "x_label": "Animal Groups",
                "img_title": "Biodiversity: Known Species by Animal Group",
            },
            {
                "bar_data": [35.8, 32.6, 29.4, 26.7, 24.3, 21.9, 19.5, 17.6, 15.8, 14.1],
                "bar_labels": ["Lion", "Tiger", "Gray Wolf", "Cheetah", "Leopard", "Puma", "Jaguar", "Spotted Hyena", "Brown Bear", "Polar Bear"],
                "bar_colors": ["#C19A6B", "#FF8C00", "#808080", "#F7C815", "#F4A460", "#A0522D", "#FFA07A", "#D3D3D3", "#8B4513", "#FFFFFF"],
                "y_label": "Hunt Success Rate (%)",
                "x_label": "Predator Species",
                "img_title": "Hunting Success Rates of Apex Predators",
            },
            {
                "bar_data": [38.6, 35.2, 32.1, 28.9, 26.4, 23.7, 21.3, 19.2, 17.4, 15.6],
                "bar_labels": ["Honey Bee", "Butterfly", "Hoverfly", "Bumblebee", "Beetle", "Wasp", "Moth", "Ant", "Fly", "Midge"],
                "bar_colors": ["#FFBF00", "#FF69B4", "#FFD700", "#000000", "#654321", "#FFFF00", "#C0C0C0", "#8B0000", "#000000", "#808080"],
                "y_label": "Crop Pollination Contribution (%)",
                "x_label": "Insect Species",
                "img_title": "Agricultural Contribution of Pollinating Insects",
            },
            {
                "bar_data": [37.5, 34.8, 32.3, 29.6, 27.1, 24.9, 22.7, 20.5, 18.6, 16.8],
                "bar_labels": ["Great Barrier Reef", "Amazon Rainforest", "Congo Basin", "Borneo Rainforest", "Coral Triangle", "Sundarbans", "Madagascar", "Galapagos Islands", "Pantanal Wetlands", "Serengeti"],
                "bar_colors": ["#00BFFF", "#228B22", "#3CB371", "#006400", "#20B2AA", "#6B8E23", "#FFA07A", "#BC8F8F", "#4682B4", "#F4A460"],
                "y_label": "Species Diversity (thousands)",
                "x_label": "Ecosystems",
                "img_title": "Biodiversity Hotspots: Animal Species Count",
            },
        ],
        "7 - Plant & Botany": [
            {
                "bar_data": [115.8, 107.3, 98.5, 92.6, 86.2, 79.4, 73.8, 68.5, 63.7, 59.2],
                "bar_labels": ["Coast Redwood", "Giant Sequoia", "Yellow Meranti", "Mountain Ash", "Sitka Spruce", "Noble Fir", "Alpine Ash", "Douglas Fir", "Kauri", "Manna Gum"],
                "bar_colors": ["#8B4513", "#A0522D", "#CD853F", "#D2691E", "#006400", "#2E8B57", "#556B2F", "#6B8E23", "#808000", "#BDB76B"],
                "y_label": "Maximum Height (meters)",
                "x_label": "Tree Species",
                "img_title": "World's Tallest Tree Species",
            },
            {
                "bar_data": [4850, 4230, 3760, 3280, 2950, 2630, 2340, 2080, 1860, 1670],
                "bar_labels": ["Great Basin Bristlecone Pine", "Alerce", "Giant Sequoia", "Huon Pine", "Rocky Mountains Bristlecone", "Sierra Juniper", "Western Redcedar", "Patagonian Cypress", "Sugi", "European Yew"],
                "bar_colors": ["#6B8E23", "#808000", "#556B2F", "#ADFF2F", "#9ACD32", "#7FFF00", "#32CD32", "#00FF00", "#008000", "#006400"],
                "y_label": "Maximum Age (years)",
                "x_label": "Tree Species",
                "img_title": "World's Longest-Living Tree Species",
            },
            {
                "bar_data": [32.7, 29.4, 26.8, 24.3, 21.9, 19.5, 17.6, 15.8, 14.2, 12.7],
                "bar_labels": ["Orchids", "Daisies", "Roses", "Lilies", "Mints", "Legumes", "Bromeliads", "Cacti", "Palms", "Grasses"],
                "bar_colors": ["#DA70D6", "#F0E68C", "#FF69B4", "#FFF0F5", "#98FB98", "#FFDAB9", "#FFB6C1", "#00FF7F", "#FF7F50", "#7CFC00"],
                "y_label": "Species Count (thousands)",
                "x_label": "Plant Families",
                "img_title": "Diversity of Plant Families",
            },
            {
                "bar_data": [48.6, 45.2, 41.9, 38.7, 35.8, 33.1, 30.6, 28.2, 26.0, 24.0],
                "bar_labels": ["Amazon Rainforest", "Congo Basin", "Southeast Asian Rainforest", "New Guinea Rainforest", "Valdivian Temperate Forest", "Eastern Australian Forests", "Sundaland", "Indo-Burma", "Mesoamerica", "Philippines"],
                "bar_colors": ["#228B22", "#006400", "#008000", "#32CD32", "#3CB371", "#2E8B57", "#6B8E23", "#556B2F", "#66CDAA", "#8FBC8F"],
                "y_label": "Plant Species (thousands)",
                "x_label": "Regions",
                "img_title": "Plant Biodiversity Hotspots",
            },
            {
                "bar_data": [96.5, 89.3, 82.7, 76.4, 70.8, 65.5, 60.7, 56.2, 52.1, 48.3],
                "bar_labels": ["Corpse Flower", "Talipot Palm", "Century Plant", "Titan Arum", "Puya Raimondii", "King Sago", "Japanese Bamboo", "Madagascan Palm", "Kurinji", "Queen of the Andes"],
                "bar_colors": ["#800020", "#2F4F4F", "#8B4513", "#A0522D", "#006400", "#008080", "#2E8B57", "#3CB371", "#6B8E23", "#556B2F"],
                "y_label": "Flowering Cycle (years)",
                "x_label": "Plant Species",
                "img_title": "Plants with Longest Flowering Cycles",
            },
            {
                "bar_data": [157.2, 143.5, 131.6, 120.3, 110.8, 101.4, 93.1, 85.7, 78.3, 71.9],
                "bar_labels": ["Rice", "Wheat", "Maize", "Soybean", "Potato", "Cassava", "Sweet Potato", "Sorghum", "Yam", "Plantain"],
                "bar_colors": ["#FFF8DC", "#F5DEB3", "#FFD700", "#FFFF00", "#B8860B", "#CD853F", "#FFA500", "#FF8C00", "#A0522D", "#FFE4B5"],
                "y_label": "Annual Production (Million Tonnes)",
                "x_label": "Crop Types",
                "img_title": "Global Production of Major Food Crops",
            },
            {
                "bar_data": [42.7, 39.5, 36.4, 33.8, 31.2, 28.9, 26.7, 24.6, 22.8, 21.0],
                "bar_labels": ["California Poppy", "Black Nightshade", "Foxglove", "Datura", "Opium Poppy", "Belladonna", "Tobacco Plant", "Castor Bean", "White Snakeroot", "Water Hemlock"],
                "bar_colors": ["#FF8C00", "#2F4F4F", "#9932CC", "#4B0082", "#FF4500", "#5F4B28", "#F1C27D", "#00FF7F", "#FFFFFF", "#48D1CC"],
                "y_label": "Toxicity Index",
                "x_label": "Plant Species",
                "img_title": "Most Toxic Plant Species",
            },
            {
                "bar_data": [6.3, 5.8, 5.4, 4.9, 4.5, 4.2, 3.8, 3.5, 3.2, 2.9],
                "bar_labels": ["Madagascar Periwinkle", "Pacific Yew", "Opium Poppy", "Willow", "Foxglove", "Cinchona", "Mayapple", "Aloe Vera", "Turmeric", "Ginseng"],
                "bar_colors": ["#FF69B4", "#006400", "#FF4500", "#6B8E23", "#9932CC", "#CD853F", "#FFFF00", "#008000", "#FFA500", "#A52A2A"],
                "y_label": "Medicinal Value Index",
                "x_label": "Plant Species",
                "img_title": "Plants with Highest Medicinal Value",
            },
            {
                "bar_data": [73.5, 67.9, 62.8, 58.1, 53.7, 49.6, 45.8, 42.3, 39.1, 36.2],
                "bar_labels": ["Cactus", "Water Lily", "Mangrove", "Desert Date", "Welwitschia", "Baobab", "Resurrection Plant", "Seagrass", "Desert Sage", "Ice Plant"],
                "bar_colors": ["#D2B48C", "#4682B4", "#008080", "#F4A460", "#B8860B", "#A52A2A", "#556B2F", "#00FFFF", "#DAA520", "#AFEEEE"],
                "y_label": "Environmental Adaptation Score",
                "x_label": "Plant Species",
                "img_title": "Plants with Extreme Environmental Adaptations",
            },
            {
                "bar_data": [64.7, 59.8, 55.4, 51.2, 47.3, 43.7, 40.5, 37.4, 34.6, 32.1],
                "bar_labels": ["Redwood", "Douglas Fir", "Oak", "Maple", "Eucalyptus", "Teak", "Bamboo", "Pine", "Mahogany", "Cedar"],
                "bar_colors": ["#8B4513", "#A0522D", "#6B4226", "#FF8C00", "#ADFF2F", "#CD853F", "#F5DEB3", "#228B22", "#800000", "#DEB887"],
                "y_label": "Carbon Sequestration (tons/hectare)",
                "x_label": "Tree Types",
                "img_title": "Carbon Sequestration by Tree Species",
            },
        ],
        "8 - Biology & Chemistry": [
            {
                "bar_data": [45.8, 41.3, 37.6, 34.2, 31.5, 28.9, 26.4, 24.1, 22.0, 20.1],
                "bar_labels": ["Bacteria", "Archaea", "Fungi", "Protists", "Plants", "Arthropods", "Mollusks", "Chordates", "Annelids", "Nematodes"],
                "bar_colors": ["#4B0082", "#9370DB", "#8B4513", "#20B2AA", "#228B22", "#FF7F50", "#FF00FF", "#1E90FF", "#FF6347", "#FFD700"],
                "y_label": "Genetic Diversity Index",
                "x_label": "Taxonomic Groups",
                "img_title": "Genetic Diversity Across Taxonomic Groups",
            },
            {
                "bar_data": [2.43, 1.89, 1.56, 1.34, 1.12, 0.98, 0.87, 0.76, 0.67, 0.58],
                "bar_labels": ["H", "C", "O", "N", "Si", "P", "S", "Al", "Na", "Ca"],
                "bar_colors": ["#00FFFF", "#2F4F4F", "#FF0000", "#0000FF", "#FF00FF", "#FF8C00", "#FFFF00", "#A9A9A9", "#00FF00", "#8A2BE2"],
                "y_label": "Abundance in Earth's Crust (%)",
                "x_label": "Elements",
                "img_title": "Most Abundant Elements in Earth's Crust",
            },
            {
                "bar_data": [165.3, 148.7, 135.2, 122.8, 112.5, 102.9, 94.1, 86.3, 78.9, 72.4],
                "bar_labels": ["Insulin", "Hemoglobin", "Collagen", "Actin", "Myosin", "Albumin", "Keratin", "Tubulin", "Elastin", "Fibrinogen"],
                "bar_colors": ["#6495ED", "#DC143C", "#D2691E", "#FF6347", "#CD5C5C", "#B0C4DE", "#8B4513", "#5F9EA0", "#FFDAB9", "#DB7093"],
                "y_label": "Molecular Weight (kDa)",
                "x_label": "Proteins",
                "img_title": "Molecular Weights of Essential Human Proteins",
            },
            {
                "bar_data": [98.7, 92.3, 85.1, 79.6, 73.8, 68.4, 63.7, 59.2, 55.1, 51.4],
                "bar_labels": ["ATP Synthesis", "Glycolysis", "Krebs Cycle", "Photosynthesis", "DNA Replication", "Protein Synthesis", "Fatty Acid Oxidation", "Gluconeogenesis", "Urea Cycle", "Pentose Phosphate Pathway"],
                "bar_colors": ["#FFD700", "#FF4500", "#32CD32", "#1E90FF", "#8A2BE2", "#FF1493", "#00CED1", "#FF7F50", "#4682B4", "#BC8F8F"],
                "y_label": "Energy Efficiency (%)",
                "x_label": "Biological Processes",
                "img_title": "Energy Efficiency of Major Biological Processes",
            },
            {
                "bar_data": [327.4, 295.8, 267.5, 242.3, 218.7, 197.6, 178.9, 162.5, 147.8, 133.9],
                "bar_labels": ["Gold", "Platinum", "Silver", "Copper", "Iron", "Aluminum", "Lead", "Zinc", "Nickel", "Tin"],
                "bar_colors": ["#FFD700", "#E5E4E2", "#C0C0C0", "#B87333", "#A19D94", "#848789", "#778899", "#ADADAD", "#727472", "#C2C3C3"],
                "y_label": "Atomic Weight (g/mol)",
                "x_label": "Metals",
                "img_title": "Atomic Weights of Common Metals",
            },
            {
                "bar_data": [3287.6, 2943.2, 2675.9, 2413.4, 2197.8, 1983.5, 1794.7, 1625.3, 1472.8, 1334.1],
                "bar_labels": ["Bacteria", "Fungi", "Protists", "Archaea", "Viruses", "Algae", "Insects", "Nematodes", "Plants", "Vertebrates"],
                "bar_colors": ["#E0115F", "#228B22", "#1E90FF", "#FF8C00", "#9932CC", "#008080", "#FF4500", "#FFD700", "#006400", "#8B0000"],
                "y_label": "Number of Species (thousands)",
                "x_label": "Taxonomic Groups",
                "img_title": "Estimated Biodiversity by Taxonomic Group",
            },
            {
                "bar_data": [7.86, 7.53, 7.21, 6.98, 6.74, 6.52, 6.31, 6.12, 5.89, 5.67],
                "bar_labels": ["Human", "Chimpanzee", "Bonobo", "Gorilla", "Orangutan", "Gibbon", "Baboon", "Macaque", "Mouse", "Rat"],
                "bar_colors": ["#FFA07A", "#8B4513", "#A0522D", "#D2691E", "#FF8C00", "#DAA520", "#CD853F", "#F4A460", "#C0C0C0", "#696969"],
                "y_label": "Genome Size (billion base pairs)",
                "x_label": "Species",
                "img_title": "Comparative Genome Sizes of Mammals",
            },
            {
                "bar_data": [185.3, 167.9, 152.4, 138.6, 125.9, 114.5, 104.1, 94.6, 86.0, 78.2],
                "bar_labels": ["Hydrogen", "Oxygen", "Carbon", "Nitrogen", "Calcium", "Phosphorus", "Potassium", "Sulfur", "Sodium", "Magnesium"],
                "bar_colors": ["#00FFFF", "#FF0000", "#2F4F4F", "#0000FF", "#8A2BE2", "#FF8C00", "#800080", "#FFFF00", "#00FF00", "#FF00FF"],
                "y_label": "Concentration in Human Body (g/kg)",
                "x_label": "Elements",
                "img_title": "Most Abundant Elements in Human Body",
            },
            {
                "bar_data": [63.8, 58.7, 54.3, 49.8, 45.9, 42.3, 39.1, 36.2, 33.4, 30.8],
                "bar_labels": ["Cytochrome P450", "Glutathione S-transferase", "Alcohol Dehydrogenase", "Aldehyde Dehydrogenase", "UDP-glucuronosyltransferase", "Carboxylesterase", "Arylamine N-acetyltransferase", "Epoxide Hydrolase", "Sulfotransferase", "Methyltransferase"],
                "bar_colors": ["#FF4500", "#32CD32", "#1E90FF", "#FF1493", "#00CED1", "#FF7F50", "#9370DB", "#20B2AA", "#FFDAB9", "#8B008B"],
                "y_label": "Metabolic Activity Rate",
                "x_label": "Enzymes",
                "img_title": "Metabolic Rates of Drug-Processing Enzymes",
            },
            {
                "bar_data": [354.7, 327.6, 302.8, 280.4, 258.2, 239.1, 220.9, 203.6, 188.2, 173.8],
                "bar_labels": ["Acetylcholine", "Dopamine", "Serotonin", "Norepinephrine", "GABA", "Glutamate", "Endorphins", "Glycine", "Histamine", "Vasopressin"],
                "bar_colors": ["#FF69B4", "#008000", "#4169E1", "#FFD700", "#FF6347", "#00FA9A", "#BA55D3", "#20B2AA", "#CD5C5C", "#4682B4"],
                "y_label": "Receptor Binding Affinity",
                "x_label": "Neurotransmitters",
                "img_title": "Binding Affinities of Major Neurotransmitters",
            },
        ],
        "9 - Food & Nutrition": [
            {
                "bar_data": [83.6, 78.2, 73.5, 68.9, 64.7, 60.4, 56.8, 52.9, 49.5, 46.3],
                "bar_labels": ["Salmon", "Spinach", "Blueberries", "Almonds", "Quinoa", "Avocado", "Sweet Potato", "Broccoli", "Greek Yogurt", "Eggs"],
                "bar_colors": ["#FF6347", "#006400", "#4169E1", "#CD853F", "#F5DEB3", "#2E8B57", "#FF8C00", "#228B22", "#F0FFF0", "#FFFACD"],
                "y_label": "Nutrient Density Score",
                "x_label": "Foods",
                "img_title": "Nutrient Density of Superfoods",
            },
            {
                "bar_data": [437.2, 389.5, 352.7, 321.4, 295.8, 267.3, 243.6, 221.9, 202.7, 185.4],
                "bar_labels": ["Dark Chocolate", "Pecans", "Acai Berries", "Russet Potato", "Artichokes", "Red Wine", "Black Tea", "Kidney Beans", "Blackberries", "Cilantro"],
                "bar_colors": ["#3B2F2F", "#A0522D", "#4B0082", "#A52A2A", "#808000", "#8B0000", "#2F4F4F", "#800000", "#000080", "#2E8B57"],
                "y_label": "Antioxidant Content (μmol/g)",
                "x_label": "Foods",
                "img_title": "Foods with Highest Antioxidant Content",
            },
            {
                "bar_data": [9.63, 8.97, 8.41, 7.86, 7.32, 6.85, 6.39, 5.97, 5.58, 5.21],
                "bar_labels": ["Beef", "Pork", "Lamb", "Chicken", "Turkey", "Fish", "Shellfish", "Milk", "Cheese", "Eggs"],
                "bar_colors": ["#8B0000", "#FFC0CB", "#F5DEB3", "#FFFACD", "#F5F5DC", "#B0E0E6", "#F08080", "#F0FFFF", "#FFEBCD", "#FFFACD"],
                "y_label": "Protein Content (g per 100g)",
                "x_label": "Animal Products",
                "img_title": "Protein Content in Animal Products",
            },
            {
                "bar_data": [325.7, 298.3, 274.1, 251.8, 231.2, 212.5, 195.3, 179.6, 165.1, 151.9],
                "bar_labels": ["Whole Milk", "Dark Chocolate", "Sardines", "Tofu", "Yogurt", "Feta Cheese", "Collard Greens", "Kale", "White Beans", "Almonds"],
                "bar_colors": ["#F0FFF0", "#3B2F2F", "#B0C4DE", "#F5F5DC", "#FFFFF0", "#F0FFFF", "#006400", "#228B22", "#F5F5DC", "#CD853F"],
                "y_label": "Calcium Content (mg per 100g)",
                "x_label": "Foods",
                "img_title": "Foods Highest in Calcium Content",
            },
            {
                "bar_data": [83.7, 76.9, 71.2, 65.4, 60.2, 55.7, 51.3, 47.5, 43.9, 40.6],
                "bar_labels": ["White Bread", "White Rice", "Potatoes", "Cornflakes", "Honey", "Watermelon", "Bagel", "Rice Cakes", "Pineapple", "Crackers"],
                "bar_colors": ["#F5F5DC", "#FFFAFA", "#A52A2A", "#F5DEB3", "#FFA500", "#FF0000", "#D2B48C", "#FFFAFA", "#FFD700", "#DEB887"],
                "y_label": "Glycemic Index",
                "x_label": "Foods",
                "img_title": "Foods with Highest Glycemic Index",
            },
            {
                "bar_data": [928.4, 864.3, 797.5, 735.2, 679.7, 627.8, 580.4, 537.2, 496.9, 458.2],
                "bar_labels": ["Olive Oil", "Avocados", "Walnuts", "Salmon", "Flaxseeds", "Chia Seeds", "Mackerel", "Almonds", "Sardines", "Dark Chocolate"],
                "bar_colors": ["#808000", "#2E8B57", "#8B4513", "#FF6347", "#CD853F", "#2F4F4F", "#4682B4", "#CD853F", "#B0C4DE", "#3B2F2F"],
                "y_label": "Healthy Fat Content (mg per 100g)",
                "x_label": "Foods",
                "img_title": "Foods Rich in Healthy Fats",
            },
            {
                "bar_data": [297.8, 276.5, 256.9, 238.8, 221.5, 206.3, 191.9, 178.4, 165.9, 154.2],
                "bar_labels": ["Coffee", "Green Tea", "Black Tea", "Energy Drinks", "Cola", "Chocolate", "Yerba Mate", "Espresso", "Guarana", "Matcha"],
                "bar_colors": ["#4A2C2A", "#008000", "#2F4F4F", "#1E90FF", "#8B4513", "#3B2F2F", "#556B2F", "#000000", "#CD853F", "#008080"],
                "y_label": "Caffeine Content (mg per 100g)",
                "x_label": "Food/Beverages",
                "img_title": "Caffeine Content in Foods and Beverages",
            },
            {
                "bar_data": [43.8, 40.1, 36.9, 33.7, 31.2, 28.5, 26.3, 24.1, 22.0, 20.3],
                "bar_labels": ["USA", "Germany", "France", "Italy", "Spain", "China", "Japan", "United Kingdom", "Brazil", "India"],
                "bar_colors": ["#3C3B6E", "#000000", "#0055A4", "#008C45", "#AA151B", "#DE2910", "#BC002D", "#012169", "#009C3B", "#FF9933"],
                "y_label": "Daily Caloric Intake (hundreds)",
                "x_label": "Countries",
                "img_title": "Average Daily Caloric Intake by Country",
            },
            {
                "bar_data": [16.9, 15.7, 14.6, 13.4, 12.5, 11.6, 10.8, 10.0, 9.3, 8.7],
                "bar_labels": ["Lentils", "Black Beans", "Chickpeas", "Kidney Beans", "Pinto Beans", "Edamame", "Green Peas", "Lima Beans", "Navy Beans", "Split Peas"],
                "bar_colors": ["#CD853F", "#000000", "#F5DEB3", "#800000", "#D2B48C", "#008000", "#98FB98", "#F5F5DC", "#FFFFFF", "#EEDD82"],
                "y_label": "Fiber Content (g per 100g)",
                "x_label": "Legumes",
                "img_title": "Fiber Content in Legumes",
            },
            {
                "bar_data": [145.8, 132.6, 120.5, 110.2, 100.9, 91.7, 84.3, 76.8, 70.3, 64.8],
                "bar_labels": ["Oysters", "Beef Liver", "Swiss Chard", "Spirulina", "Octopus", "Shiitake Mushrooms", "Cashews", "Turkey", "Pumpkin Seeds", "Spinach"],
                "bar_colors": ["#E0FFFF", "#8B0000", "#008000", "#00CED1", "#FF6347", "#8B4513", "#D2B48C", "#F5F5DC", "#2F4F4F", "#006400"],
                "y_label": "Zinc Content (mg per 100g)",
                "x_label": "Foods",
                "img_title": "Foods Highest in Zinc Content",
            },
        ],
        "10 - Space & Astronomy": [
            {
                "bar_data": [142984.0, 120536.0, 50724.0, 49244.0, 87232.0, 57.9, 58.2, 25.4, 2.8, 1.3],
                "bar_labels": ["Jupiter", "Saturn", "Uranus", "Neptune", "UY Scuti", "Wolf 359", "Proxima Centauri", "Sirius", "Sun", "Earth"],
                "bar_colors": ["#E3A857", "#EAD6B8", "#6BCAE2", "#2B4F81", "#FF6347", "#FF4500", "#FF8C00", "#00BFFF", "#FFD700", "#1E90FF"],
                "y_label": "Diameter (thousands of km)",
                "x_label": "Celestial Bodies",
                "img_title": "Size Comparison of Celestial Bodies",
            },
            {
                "bar_data": [4.37, 7.76, 10.66, 13.14, 15.98, 18.76, 21.53, 24.25, 26.92, 29.85],
                "bar_labels": ["Proxima Centauri", "Sirius", "Tau Ceti", "Vega", "Altair", "Fomalhaut", "Pollux", "Castor", "Bellatrix", "Spica"],
                "bar_colors": ["#FF4500", "#00BFFF", "#FF69B4", "#00FF00", "#FFD700", "#7FFFD4", "#FF8C00", "#BA55D3", "#4169E1", "#32CD32"],
                "y_label": "Distance from Earth (light years)",
                "x_label": "Stars",
                "img_title": "Nearest Stars to Earth",
            },
            {
                "bar_data": [13.8, 11.2, 9.5, 8.3, 7.4, 6.2, 4.9, 3.7, 2.5, 1.6],
                "bar_labels": ["Universe Age", "Oldest Star", "Milky Way", "Solar System", "Earth", "First Multicellular Life", "Dinosaurs", "First Primates", "Earliest Humans", "Human Civilization"],
                "bar_colors": ["#000000", "#FFD700", "#E6E6FA", "#1E90FF", "#4169E1", "#008000", "#8B4513", "#A0522D", "#CD853F", "#F5DEB3"],
                "y_label": "Age (billion years)",
                "x_label": "Cosmic Timeline",
                "img_title": "Cosmic Timeline: Age of Astronomical Objects",
            },
            {
                "bar_data": [5.972, 1.898, 5.683, 8.681, 10.244, 0.330, 0.815, 0.107, 0.073, 0.012],
                "bar_labels": ["Earth", "Jupiter", "Saturn", "Uranus", "Neptune", "Mercury", "Venus", "Mars", "Moon", "Pluto"],
                "bar_colors": ["#1E90FF", "#E3A857", "#EAD6B8", "#6BCAE2", "#2B4F81", "#C0C0C0", "#FFCC99", "#FF4500", "#F5F5DC", "#CDC5BF"],
                "y_label": "Mass (x10²⁴ kg)",
                "x_label": "Planets/Celestial Bodies",
                "img_title": "Mass of Solar System Bodies",
            },
            {
                "bar_data": [687.0, 365.3, 224.7, 88.0, 29.5, 11.9, 10.7, 4332.0, 60190.0, 90560.0],
                "bar_labels": ["Mars", "Earth", "Venus", "Mercury", "Saturn", "Jupiter", "Uranus", "Proxima b", "Kepler-452b", "HD 189733b"],
                "bar_colors": ["#FF4500", "#1E90FF", "#FFCC99", "#C0C0C0", "#EAD6B8", "#E3A857", "#6BCAE2", "#FF69B4", "#00FF00", "#FFD700"],
                "y_label": "Orbital Period (Earth days)",
                "x_label": "Planets",
                "img_title": "Orbital Periods of Planets",
            },
            {
                "bar_data": [5772.0, 12000.0, 22000.0, 9940.0, 3590.0, 2860.0, 3380.0, 4450.0, 30000.0, 33000.0],
                "bar_labels": ["Sun", "Sirius A", "Vega", "Procyon A", "Altair", "Alpha Centauri A", "Fomalhaut", "Deneb", "Betelgeuse", "Antares"],
                "bar_colors": ["#FFD700", "#00BFFF", "#00FF00", "#FF69B4", "#FFD700", "#7FFFD4", "#FF8C00", "#BA55D3", "#FF4500", "#8B0000"],
                "y_label": "Surface Temperature (Kelvin)",
                "x_label": "Stars",
                "img_title": "Surface Temperatures of Stars",
            },
            {
                "bar_data": [1, 8, 95, 200, 1300, 5400, 10000, 125000, 250000, 400000],
                "bar_labels": ["Milky Way", "Local Group", "Virgo Supercluster", "Cosmic Web", "Observable Universe", "Planck Length", "Proton", "Human Scale", "Earth", "Solar System"],
                "bar_colors": ["#E6E6FA", "#4169E1", "#1E90FF", "#00BFFF", "#87CEEB", "#FF4500", "#FF8C00", "#FFD700", "#1E90FF", "#4169E1"],
                "y_label": "Scale (log₁₀ meters)",
                "x_label": "Astronomical Structures",
                "img_title": "Scale of Astronomical Structures",
            },
            {
                "bar_data": [100.0, 91.8, 84.3, 77.5, 71.2, 65.3, 59.8, 54.6, 49.9, 45.4],
                "bar_labels": ["Big Bang", "Cosmic Inflation", "Primordial Nucleosynthesis", "Recombination", "Dark Ages", "First Stars", "Reionization", "Galaxy Formation", "Solar System Formation", "Present Day"],
                "bar_colors": ["#000000", "#191970", "#483D8B", "#6A5ACD", "#7B68EE", "#8A2BE2", "#9370DB", "#BA55D3", "#DA70D6", "#EE82EE"],
                "y_label": "Energy Density (relative units)",
                "x_label": "Cosmic Epochs",
                "img_title": "Energy Density Through Cosmic History",
            },
            {
                "bar_data": [379.4, 342.7, 308.9, 276.8, 248.1, 223.2, 199.9, 179.3, 161.8, 145.6],
                "bar_labels": ["Voyager 1", "Voyager 2", "Pioneer 10", "Pioneer 11", "New Horizons", "Parker Solar Probe", "Juno", "Cassini", "Galileo", "Curiosity"],
                "bar_colors": ["#4169E1", "#1E90FF", "#00BFFF", "#87CEEB", "#ADD8E6", "#B0E0E6", "#AFEEEE", "#E0FFFF", "#F0FFFF", "#F5FFFA"],
                "y_label": "Mission Distance (AU)",
                "x_label": "Space Missions",
                "img_title": "Farthest Space Missions from Earth",
            },
            {
                "bar_data": [2950.0, 2430.0, 2370.0, 2270.0, 1850.0, 1560.0, 1430.0, 1210.0, 940.0, 780.0],
                "bar_labels": ["TON 618", "S5 0014+81", "SDSS J102325.31+514251.0", "SDSS J140821.67+025733.2", "SDSS J013127.34−032100.1", "Sombrero Galaxy", "Messier 87", "Andromeda Galaxy", "Milky Way", "Triangulum Galaxy"],
                "bar_colors": ["#000000", "#191970", "#483D8B", "#6A5ACD", "#7B68EE", "#8A2BE2", "#9370DB", "#BA55D3", "#E6E6FA", "#D8BFD8"],
                "y_label": "Mass (billions of solar masses)",
                "x_label": "Galaxies/Black Holes",
                "img_title": "Mass of Supermassive Black Holes and Galaxies",
            },
        ],
        "11 - Sale & Merchandise": [
            {
                "bar_data": [386.2, 342.8, 305.6, 271.4, 243.8, 218.7, 197.3, 178.6, 159.2, 143.7],
                "bar_labels": ["Electronics", "Clothing", "Home Goods", "Beauty Products", "Sporting Goods", "Books", "Toys", "Jewelry", "Furniture", "Automotive"],
                "bar_colors": ["#4285F4", "#EA4335", "#FBBC05", "#34A853", "#FF6D01", "#46A2D9", "#A142F4", "#D4AF37", "#8B4513", "#C0C0C0"],
                "y_label": "Annual Sales ($ Billion)",
                "x_label": "Product Categories",
                "img_title": "Annual Sales by Product Category",
            },
            {
                "bar_data": [37.8, 34.2, 31.5, 28.9, 26.4, 24.1, 22.3, 20.7, 18.9, 17.2],
                "bar_labels": ["Black Friday", "Cyber Monday", "Singles' Day", "Prime Day", "Boxing Day", "Back to School", "Mother's Day", "Father's Day", "Valentine's Day", "Easter"],
                "bar_colors": ["#000000", "#00AAFF", "#FF0000", "#FF9900", "#008000", "#FFA500", "#FF69B4", "#4169E1", "#FF1493", "#FFFF00"],
                "y_label": "Sales Volume ($ Billion)",
                "x_label": "Shopping Events",
                "img_title": "Global Sales Volume by Shopping Event",
            },
            {
                "bar_data": [98.7, 90.4, 82.6, 75.3, 68.9, 62.1, 56.8, 51.4, 46.7, 42.3],
                "bar_labels": ["Amazon", "Walmart", "Alibaba", "eBay", "JD.com", "Target", "Costco", "Best Buy", "Home Depot", "Wayfair"],
                "bar_colors": ["#FF9900", "#004C91", "#FF6600", "#E53238", "#D71C06", "#CC0000", "#003DA6", "#0046BE", "#F96302", "#7B1FA2"],
                "y_label": "E-commerce Revenue ($ Billion)",
                "x_label": "Retailers",
                "img_title": "E-commerce Revenue by Major Retailers",
            },
            {
                "bar_data": [48.3, 43.6, 39.2, 35.4, 32.1, 28.9, 26.3, 23.8, 21.6, 19.5],
                "bar_labels": ["Nike", "Adidas", "Louis Vuitton", "Gucci", "Hermès", "Chanel", "Zara", "H&M", "Uniqlo", "Lululemon"],
                "bar_colors": ["#FF6D01", "#000000", "#C74634", "#00FF00", "#FF9900", "#000000", "#1E8AD3", "#E50010", "#FF0000", "#D31F3C"],
                "y_label": "Brand Value ($ Billion)",
                "x_label": "Fashion Brands",
                "img_title": "Global Fashion Brand Values",
            },
            {
                "bar_data": [67.5, 62.1, 56.8, 52.4, 48.3, 44.6, 40.9, 37.5, 34.2, 31.3],
                "bar_labels": ["Q4", "Q3", "Q2", "Q1", "December", "November", "October", "August", "July", "September"],
                "bar_colors": ["#003366", "#336699", "#6699CC", "#99CCFF", "#CC0000", "#FF9900", "#FFCC00", "#99CC00", "#CC9900", "#FF6600"],
                "y_label": "Sales Volume ($ Billion)",
                "x_label": "Time Periods",
                "img_title": "Retail Sales Distribution by Time Period",
            },
            {
                "bar_data": [42.8, 38.5, 34.9, 31.6, 28.4, 25.7, 23.2, 21.1, 19.3, 17.6],
                "bar_labels": ["Free Shipping", "Percentage Off", "BOGO", "Flash Sale", "Loyalty Points", "Seasonal Discounts", "Bundle Offers", "First-time Buyer", "Referral Bonus", "Clearance"],
                "bar_colors": ["#4285F4", "#EA4335", "#FBBC05", "#34A853", "#FF6D01", "#8B008B", "#FF7F50", "#00CED1", "#FF1493", "#ADFF2F"],
                "y_label": "Conversion Rate (%)",
                "x_label": "Promotion Types",
                "img_title": "Effectiveness of Different Promotion Types",
            },
            {
                "bar_data": [285.6, 257.3, 232.4, 208.9, 188.7, 169.8, 153.2, 138.4, 124.6, 112.7],
                "bar_labels": ["North America", "Europe", "East Asia", "Southeast Asia", "South America", "Oceania", "Middle East", "South Asia", "Africa", "Central America"],
                "bar_colors": ["#B22234", "#003399", "#DE2910", "#FFD700", "#009B3A", "#00008B", "#006C35", "#FF9933", "#008751", "#007934"],
                "y_label": "E-commerce Sales ($ Billion)",
                "x_label": "Regions",
                "img_title": "E-commerce Sales by Global Region",
            },
            {
                "bar_data": [87.3, 79.6, 72.8, 66.5, 60.8, 55.4, 50.7, 46.3, 42.1, 38.5],
                "bar_labels": ["Smartphones", "Laptops", "Televisions", "Tablets", "Smartwatches", "Gaming Consoles", "Headphones", "Cameras", "Smart Speakers", "Fitness Trackers"],
                "bar_colors": ["#A4C639", "#00ADEF", "#E50914", "#FF9900", "#5AC8FA", "#107C10", "#FF6D01", "#FC0019", "#00AAFF", "#00B2A9"],
                "y_label": "Units Sold (Millions)",
                "x_label": "Electronics Categories",
                "img_title": "Global Electronics Sales by Category",
            },
            {
                "bar_data": [56.7, 51.4, 46.8, 42.5, 38.6, 35.1, 32.2, 29.3, 26.7, 24.3],
                "bar_labels": ["Credit Card", "Digital Wallet", "Debit Card", "Bank Transfer", "PayPal", "Mobile Payment", "Buy Now Pay Later", "Gift Cards", "Crypto", "Cash on Delivery"],
                "bar_colors": ["#FF5F00", "#2196F3", "#4CAF50", "#9C27B0", "#003087", "#4285F4", "#00C244", "#F4511E", "#F7931A", "#795548"],
                "y_label": "Transaction Volume (%)",
                "x_label": "Payment Methods",
                "img_title": "E-commerce Payment Method Preferences",
            },
            {
                "bar_data": [42.3, 38.6, 35.7, 32.9, 30.1, 27.8, 25.4, 23.3, 21.5, 19.8],
                "bar_labels": ["Apparel", "Accessories", "Footwear", "Electronics", "Beauty", "Home Decor", "Kitchenware", "Outdoor Gear", "Sports Equipment", "Office Supplies"],
                "bar_colors": ["#FF4081", "#9C27B0", "#3F51B5", "#03A9F4", "#FF9800", "#795548", "#607D8B", "#4CAF50", "#FFC107", "#9E9E9E"],
                "y_label": "Return Rate (%)",
                "x_label": "Product Categories",
                "img_title": "Product Return Rates by Category",
            },
        ],
        "12 - Market & Economy": [
            {
                "bar_data": [25.87, 21.43, 16.72, 14.98, 12.53, 9.86, 7.24, 5.68, 4.31, 3.27],
                "bar_labels": ["United States", "China", "Japan", "Germany", "United Kingdom", "India", "France", "Italy", "Canada", "South Korea"],
                "bar_colors": ["#3C3B6E", "#DE2910", "#BC002D", "#000000", "#012169", "#FF9933", "#002395", "#009246", "#FF0000", "#0047A0"],
                "y_label": "GDP ($ Trillion)",
                "x_label": "Countries",
                "img_title": "Top 10 Countries by GDP",
            },
            {
                "bar_data": [28.5, 25.7, 23.2, 20.9, 18.6, 16.4, 14.3, 12.5, 10.8, 9.3],
                "bar_labels": ["Technology", "Healthcare", "Consumer Discretionary", "Financial Services", "Communications", "Industrials", "Consumer Staples", "Utilities", "Energy", "Materials"],
                "bar_colors": ["#0071C5", "#FF4081", "#FF9800", "#673AB7", "#3F51B5", "#FFC107", "#4CAF50", "#795548", "#F44336", "#607D8B"],
                "y_label": "Market Capitalization ($ Trillion)",
                "x_label": "Sectors",
                "img_title": "Global Market Capitalization by Sector",
            },
            {
                "bar_data": [12.7, 11.3, 9.8, 8.6, 7.5, 6.2, 5.4, 4.7, 3.9, 3.2],
                "bar_labels": ["Luxembourg", "Ireland", "Switzerland", "Norway", "United States", "Iceland", "Denmark", "Australia", "Netherlands", "Sweden"],
                "bar_colors": ["#D22730", "#169B62", "#FF0000", "#BA0C2F", "#3C3B6E", "#003897", "#C60C30", "#00008B", "#AE1C28", "#006AA7"],
                "y_label": "GDP per Capita ($ Ten Thousand)",
                "x_label": "Countries",
                "img_title": "Countries with Highest GDP per Capita",
            },
            {
                "bar_data": [37.8, 33.6, 29.5, 26.2, 23.1, 20.7, 18.5, 16.3, 14.7, 13.1],
                "bar_labels": ["S&P 500", "NASDAQ", "Dow Jones", "FTSE 100", "Nikkei 225", "DAX", "Shanghai Composite", "Hang Seng", "CAC 40", "KOSPI"],
                "bar_colors": ["#4169E1", "#33A1DE", "#2E5090", "#0018A8", "#D00000", "#0063A6", "#DE2910", "#BF0000", "#003DA5", "#0054A6"],
                "y_label": "Annual Return (%)",
                "x_label": "Stock Indices",
                "img_title": "Annual Returns of Major Stock Indices",
            },
            {
                "bar_data": [9.8, 8.6, 7.4, 6.5, 5.7, 4.9, 4.2, 3.7, 3.3, 2.9],
                "bar_labels": ["South Africa", "Brazil", "India", "Turkey", "Russia", "Argentina", "Colombia", "Mexico", "Indonesia", "Philippines"],
                "bar_colors": ["#007A4D", "#009C3B", "#FF9933", "#E30A17", "#0039A6", "#75AADB", "#FCD116", "#006847", "#FF0000", "#0038A8"],
                "y_label": "Inflation Rate (%)",
                "x_label": "Countries",
                "img_title": "Countries with Highest Inflation Rates",
            },
            {
                "bar_data": [3.68, 3.47, 3.25, 3.06, 2.89, 2.73, 2.58, 2.44, 2.31, 2.18],
                "bar_labels": ["Switzerland", "Japan", "Germany", "United Kingdom", "United States", "France", "Canada", "Australia", "Sweden", "Netherlands"],
                "bar_colors": ["#FF0000", "#BC002D", "#000000", "#012169", "#3C3B6E", "#002395", "#FF0000", "#00008B", "#006AA7", "#AE1C28"],
                "y_label": "10-Year Government Bond Yield (%)",
                "x_label": "Countries",
                "img_title": "Government Bond Yields by Country",
            },
            {
                "bar_data": [65.7, 60.3, 55.2, 50.4, 46.1, 42.3, 38.8, 35.7, 32.9, 30.2],
                "bar_labels": ["Venture Capital", "Private Equity", "Hedge Funds", "Real Estate", "Angel Investment", "Infrastructure", "Natural Resources", "Distressed Debt", "Mezzanine Finance", "Fund of Funds"],
                "bar_colors": ["#4CAF50", "#2196F3", "#9C27B0", "#FF5722", "#FFC107", "#795548", "#3F51B5", "#F44336", "#CDDC39", "#607D8B"],
                "y_label": "Annual Return (%)",
                "x_label": "Investment Categories",
                "img_title": "Alternative Investment Returns by Category",
            },
            {
                "bar_data": [24.7, 22.1, 19.8, 17.6, 15.9, 14.2, 12.8, 11.5, 10.3, 9.2],
                "bar_labels": ["Japan", "Italy", "Portugal", "Greece", "United States", "France", "Spain", "United Kingdom", "Canada", "Germany"],
                "bar_colors": ["#BC002D", "#009246", "#FF0000", "#0D5EAF", "#3C3B6E", "#002395", "#AA151B", "#012169", "#FF0000", "#000000"],
                "y_label": "Debt to GDP Ratio (%)",
                "x_label": "Countries",
                "img_title": "Government Debt to GDP Ratios by Country",
            },
            {
                "bar_data": [9.47, 8.75, 8.12, 7.53, 6.97, 6.47, 5.98, 5.53, 5.12, 4.75],
                "bar_labels": ["South Africa", "Spain", "Italy", "Brazil", "Colombia", "Turkey", "Argentina", "Greece", "Croatia", "Latvia"],
                "bar_colors": ["#007A4D", "#AA151B", "#009246", "#009C3B", "#FCD116", "#E30A17", "#75AADB", "#0D5EAF", "#FF0000", "#A4343A"],
                "y_label": "Unemployment Rate (%)",
                "x_label": "Countries",
                "img_title": "Countries with Highest Unemployment Rates",
            },
            {
                "bar_data": [387.4, 348.7, 314.2, 283.6, 255.7, 230.2, 207.6, 187.3, 168.6, 152.1],
                "bar_labels": ["Equities", "Fixed Income", "Real Estate", "Commodities", "Private Equity", "Hedge Funds", "Venture Capital", "Cash Equivalents", "Precious Metals", "Cryptocurrencies"],
                "bar_colors": ["#4CAF50", "#2196F3", "#FF5722", "#FFC107", "#9C27B0", "#607D8B", "#3F51B5", "#CDDC39", "#FFD700", "#FF9900"],
                "y_label": "Asset Under Management ($ Trillion)",
                "x_label": "Asset Classes",
                "img_title": "Global Assets Under Management by Class",
            },
        ],
        "13 - Sports & Athletics": [
            {
                "bar_data": [39, 38, 27, 22, 20, 19, 17, 10, 10, 9],
                "bar_labels": ["USA", "China", "Japan", "UK", "ROC", "Australia", "Netherlands", "France", "Germany", "Italy"],
                "bar_colors": ["#E63946", "#457B9D", "#A8DADC", "#F4A261", "#2A9D8F", "#264653", "#FFB703", "#8ECAE6", "#023047", "#FB8500"],
                "y_label": "Gold Medals",
                "x_label": "Country",
                "img_title": "Olympic Gold Medals by Country - Tokyo 2020"
            },
            {
                "bar_data": [9.58, 9.63, 9.69, 9.72, 9.74, 9.76, 9.78, 9.79, 9.80, 9.81],
                "bar_labels": ["Usain Bolt", "Tyson Gay", "Yohan Blake", "Asafa Powell", "Justin Gatlin", "Nesta Carter", "Trayvon Bromell", "Fred Kerley", "Andre De Grasse", "Christian Coleman"],
                "bar_colors": ["#1D3557", "#E63946", "#F1FAEE", "#A8DADC", "#2A9D8F", "#F4A261", "#E9C46A", "#8D99AE", "#D00000", "#118AB2"],
                "y_label": "Time (seconds)",
                "x_label": "Athlete",
                "img_title": "Fastest 100m Sprint Times in History (Men)"
            },
            {
                "bar_data": [3.5, 2.5, 2.0, 1.5, 1.0, 0.9, 0.875, 0.8, 0.6, 0.5],
                "bar_labels": ["Soccer", "Cricket", "Hockey", "Tennis", "Volleyball", "Table Tennis", "Baseball", "Golf", "Basketball", "American Football"],
                "bar_colors": ["#003F5C", "#58508D", "#BC5090", "#FF6361", "#FFA600", "#2F4B7C", "#F95D6A", "#A05195", "#D45087", "#665191"],
                "y_label": "Fanbase (Billions)",
                "x_label": "Sport",
                "img_title": "Most Popular Sports by Global Fanbase"
            },
            {
                "bar_data": [8.32, 7.22, 6.5, 5.97, 4.4, 3.26, 2.9, 2.1, 1.75, 1.2],
                "bar_labels": ["NBA", "MLB", "EPL", "NFL", "NHL", "Serie A", "La Liga", "Bundesliga", "IPL", "MLS"],
                "bar_colors": ["#F94144", "#F3722C", "#F8961E", "#F9844A", "#F9C74F", "#90BE6D", "#43AA8B", "#4D908E", "#577590", "#277DA1"],
                "y_label": "Average Salary (Million USD)",
                "x_label": "League",
                "img_title": "Average Player Salaries in Major Sports Leagues"
            },
            {
                "bar_data": [121.01, 122.10, 122.23, 122.40, 122.50, 122.57, 123.12, 123.45, 123.60, 123.75],
                "bar_labels": ["Eliud Kipchoge", "Kelvin Kiptum", "Birhanu Legese", "Mosinet Geremew", "Dennis Kimetto", "Wilson Kipsang", "Geoffrey Mutai", "Tsegaye Mekonnen", "Mule Wasihun", "Tamirat Tola"],
                "bar_colors": ["#F94144", "#F3722C", "#F8961E", "#F9844A", "#F9C74F", "#90BE6D", "#43AA8B", "#4D908E", "#577590", "#277DA1"],
                "y_label": "Time (Minutes)",
                "x_label": "Runner",
                "img_title": "Top 10 Fastest Men's Marathon Times in History"
            },
            {
                "bar_data": [5, 4, 4, 2, 2, 1, 1, 1, 1, 1],
                "bar_labels": ["Brazil", "Germany", "Italy", "France", "Argentina", "Spain", "England", "Uruguay", "USA", "Netherlands"],
                "bar_colors": ["#FFD700", "#C0C0C0", "#CD7F32", "#F94144", "#90BE6D", "#577590", "#F3722C", "#F9844A", "#43AA8B", "#277DA1"],
                "y_label": "Titles",
                "x_label": "Country",
                "img_title": "FIFA World Cup Titles by Country"
            },
            {
                "bar_data": [136.0, 130.0, 120.0, 115.0, 100.0, 95.0, 90.0, 85.0, 82.0, 80.0],
                "bar_labels": ["Cristiano Ronaldo", "Lionel Messi", "Kylian Mbappé", "LeBron James", "Stephen Curry", "Roger Federer", "Canelo Alvarez", "Kevin Durant", "Giannis Antetokounmpo", "Tom Brady"],
                "bar_colors": ["#EF476F", "#FFD166", "#06D6A0", "#118AB2", "#073B4C", "#F94144", "#F8961E", "#43AA8B", "#577590", "#277DA1"],
                "y_label": "Earnings (Million USD)",
                "x_label": "Athlete",
                "img_title": "Top 10 Highest Paid Athletes in 2024"
            },
            {
                "bar_data": [1.5, 1.2, 0.9, 0.8, 0.75, 0.65, 0.6, 0.5, 0.48, 0.45],
                "bar_labels": ["FIFA World Cup Final", "Olympics Opening", "Super Bowl", "Champions League Final", "ICC Cricket Final", "NBA Finals", "Wimbledon Final", "Tour de France", "F1 Grand Prix", "UEFA Euro Final"],
                "bar_colors": ["#6A0572", "#AB83A1", "#F3722C", "#118AB2", "#FFD166", "#06D6A0", "#F94144", "#90BE6D", "#577590", "#2A9D8F"],
                "y_label": "Viewers (Billions)",
                "x_label": "Event",
                "img_title": "Most Watched Sporting Events Worldwide (2023)"
            },
            {
                "bar_data": [71365, 61121, 53089, 48233, 44211, 41000, 39900, 38200, 36444, 35100],
                "bar_labels": ["NFL", "Bundesliga", "EPL", "La Liga", "Serie A", "MLB", "NBA", "NHL", "MLS", "IPL"],
                "bar_colors": ["#E63946", "#F1FAEE", "#A8DADC", "#457B9D", "#1D3557", "#F3722C", "#06D6A0", "#118AB2", "#2A9D8F", "#F9C74F"],
                "y_label": "Average Attendance",
                "x_label": "League",
                "img_title": "Average Match Attendance by Sports League"
            },
            {
                "bar_data": [50, 47, 44, 38, 33, 30, 28, 26, 24, 22],
                "bar_labels": ["Athletics", "Swimming", "Cycling", "Wrestling", "Gymnastics", "Shooting", "Rowing", "Fencing", "Canoeing", "Boxing"],
                "bar_colors": ["#6A0572", "#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF", "#FF922B", "#1982C4", "#8D99AE", "#D00000", "#F15BB5"],
                "y_label": "Number of Events",
                "x_label": "Sport",
                "img_title": "Olympic Sports with the Most Events (2024)"
            },
        ],
        "14 - Computing & Technology": [
            {
                "bar_data": [43.2, 32.5, 27.8, 21.3, 18.6, 14.7, 11.5, 10.2, 9.1, 7.9],
                "bar_labels": ["Python", "JavaScript", "Java", "C#", "C++", "TypeScript", "Go", "Ruby", "PHP", "Rust"],
                "bar_colors": ["#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF", "#A061F6", "#F15BB5", "#00BBF9", "#9B5DE5", "#FF9F1C", "#3A86FF"],
                "y_label": "Popularity Index",
                "x_label": "Programming Language",
                "img_title": "Top 10 Most Popular Programming Languages (2025)"
            },
            {
                "bar_data": [65.2, 61.4, 59.7, 58.3, 56.8, 54.6, 52.3, 50.9, 49.0, 47.5],
                "bar_labels": ["Windows", "Android", "iOS", "macOS", "Linux", "Chrome OS", "HarmonyOS", "KaiOS", "Ubuntu Touch", "Tizen"],
                "bar_colors": ["#0078D7", "#A4C639", "#999999", "#B6B6B6", "#FF6F61", "#FFA500", "#8FBC8F", "#D2691E", "#6A5ACD", "#4682B4"],
                "y_label": "Global Market Share (%)",
                "x_label": "Operating System",
                "img_title": "Operating System Market Share Worldwide (2025)"
            },
            {
                "bar_data": [150.3, 143.7, 139.2, 132.8, 129.5, 123.0, 117.6, 114.0, 110.5, 105.1],
                "bar_labels": ["Apple", "Samsung", "Microsoft", "Alphabet", "Amazon", "Meta", "Tencent", "TSMC", "NVIDIA", "Intel"],
                "bar_colors": ["#A2D2FF", "#FFC8DD", "#BDE0FE", "#FFAFCC", "#CDB4DB", "#B5E48C", "#FFB703", "#8ECAE6", "#2A9D8F", "#FB8500"],
                "y_label": "Market Capitalization (Billion USD)",
                "x_label": "Company",
                "img_title": "Top 10 Most Valuable Tech Companies by Market Cap (2025)"
            },
            {
                "bar_data": [98, 92, 88, 83, 79, 75, 71, 68, 64, 60],
                "bar_labels": ["Wi-Fi", "Bluetooth", "5G", "Ethernet", "NFC", "Zigbee", "LoRa", "Z-Wave", "Infrared", "UWB"],
                "bar_colors": ["#D00000", "#FFBA08", "#3F88C5", "#032B43", "#136F63", "#F77F00", "#FFD60A", "#5F0F40", "#A3BCB6", "#9A031E"],
                "y_label": "Adoption Score",
                "x_label": "Wireless Technology",
                "img_title": "Adoption of Wireless Communication Technologies"
            },
            {
                "bar_data": [68.1, 61.7, 56.2, 52.8, 49.5, 47.3, 45.0, 42.2, 40.5, 38.0],
                "bar_labels": ["Chrome", "Safari", "Edge", "Firefox", "Samsung Internet", "Opera", "Brave", "Vivaldi", "Tor", "UC Browser"],
                "bar_colors": ["#4285F4", "#7F7FFF", "#00A4EF", "#FF7139", "#1428A0", "#FF1B2D", "#FB5607", "#3A86FF", "#8338EC", "#FFBE0B"],
                "y_label": "Browser Usage (%)",
                "x_label": "Browser",
                "img_title": "Most Used Web Browsers (2025)"
            },
            {
                "bar_data": [87.4, 80.1, 75.8, 72.3, 68.9, 65.2, 61.8, 58.0, 55.4, 51.7],
                "bar_labels": ["Google", "YouTube", "Facebook", "Instagram", "TikTok", "WhatsApp", "Amazon", "Wikipedia", "Twitter", "Reddit"],
                "bar_colors": ["#4285F4", "#FF0000", "#1877F2", "#C13584", "#69C9D0", "#25D366", "#FF9900", "#1A1A1A", "#1DA1F2", "#FF4500"],
                "y_label": "Monthly Active Users (Millions)",
                "x_label": "Platform",
                "img_title": "Most Visited Websites and Apps by Monthly Users"
            },
            {
                "bar_data": [12.5, 11.3, 10.8, 10.0, 9.4, 8.7, 8.1, 7.6, 7.0, 6.4],
                "bar_labels": ["AWS", "Azure", "Google Cloud", "Alibaba Cloud", "IBM Cloud", "Oracle Cloud", "Salesforce", "Tencent Cloud", "DigitalOcean", "Linode"],
                "bar_colors": ["#FF6F61", "#6A0572", "#4D96FF", "#B5179E", "#4361EE", "#F15BB5", "#3A86FF", "#7209B7", "#FFB703", "#118AB2"],
                "y_label": "Cloud Market Share (%)",
                "x_label": "Provider",
                "img_title": "Global Cloud Infrastructure Market Share"
            },
            {
                "bar_data": [18.3, 15.9, 14.4, 13.0, 12.1, 11.5, 10.3, 9.8, 9.1, 8.5],
                "bar_labels": ["Apple A17", "Snapdragon 8 Gen 3", "Exynos 2400", "Dimensity 9300", "Google Tensor G3", "Kirin 9000S", "Snapdragon 7+ Gen 2", "Apple M2", "Samsung 2200", "MediaTek Helio G99"],
                "bar_colors": ["#1D3557", "#FF6B6B", "#2A9D8F", "#F4A261", "#8D99AE", "#F72585", "#E63946", "#FFC300", "#5A189A", "#D00000"],
                "y_label": "Benchmark Score (in Thousands)",
                "x_label": "Mobile Processor",
                "img_title": "Top Mobile Chipsets by Benchmark Score (2025)"
            },
            {
                "bar_data": [84, 79, 76, 74, 71, 68, 66, 62, 59, 56],
                "bar_labels": ["Phishing", "Ransomware", "Malware", "DDoS Attacks", "Man-in-the-Middle", "Zero-Day Exploits", "Spyware", "SQL Injection", "Credential Stuffing", "Drive-by Downloads"],
                "bar_colors": ["#D62828", "#F77F00", "#FCBF49", "#EAE2B7", "#003049", "#780000", "#C1121F", "#669BBC", "#6A0572", "#118AB2"],
                "y_label": "Threat Severity Score",
                "x_label": "Cyber Threat",
                "img_title": "Most Common Cybersecurity Threats in 2025"
            },
            {
                "bar_data": [3.6, 3.2, 2.8, 2.4, 2.2, 2.0, 1.9, 1.8, 1.6, 1.5],
                "bar_labels": ["AI & ML", "Cybersecurity", "Cloud Computing", "Data Science", "Blockchain", "IoT", "DevOps", "AR/VR", "Quantum Computing", "Edge Computing"],
                "bar_colors": ["#6A0572", "#00B4D8", "#FFD60A", "#F94144", "#F8961E", "#6BCB77", "#118AB2", "#B5179E", "#3A86FF", "#FF006E"],
                "y_label": "Projected Investment (Trillion USD)",
                "x_label": "Technology Area",
                "img_title": "Top Tech Investment Sectors (Projected for 2030)"
            }
        ],
        "15 - Health & Medicine": [
            {
                "bar_data": [85.6, 82.3, 80.1, 78.9, 77.5, 75.2, 74.0, 72.3, 71.1, 69.8],
                "bar_labels": ["Japan", "Switzerland", "Singapore", "Australia", "Spain", "Italy", "Iceland", "South Korea", "Norway", "France"],
                "bar_colors": ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93", "#FF924C", "#9D4EDD", "#2EC4B6", "#E76F51", "#00B4D8"],
                "y_label": "Average Life Expectancy (Years)",
                "x_label": "Country",
                "img_title": "Countries with Highest Life Expectancy (2025)"
            },
            {
                "bar_data": [38.7, 36.5, 34.8, 32.4, 31.0, 28.9, 27.6, 26.3, 25.0, 23.7],
                "bar_labels": ["Heart Disease", "Stroke", "Lower Respiratory", "Alzheimer's", "Lung Cancer", "Diabetes", "Kidney Disease", "Flu/Pneumonia", "Hypertension", "Liver Disease"],
                "bar_colors": ["#D62828", "#F77F00", "#FCBF49", "#EAE2B7", "#003049", "#780000", "#C1121F", "#669BBC", "#6A0572", "#118AB2"],
                "y_label": "Annual Mortality (Millions)",
                "x_label": "Cause of Death",
                "img_title": "Top Global Causes of Death"
            },
            {
                "bar_data": [91.0, 89.4, 87.6, 86.2, 84.8, 83.5, 82.3, 80.9, 79.2, 77.5],
                "bar_labels": ["Measles", "Polio", "Smallpox", "Diphtheria", "Tetanus", "Rubella", "Hepatitis B", "HPV", "Influenza", "Mumps"],
                "bar_colors": ["#F72585", "#7209B7", "#3A0CA3", "#4361EE", "#4CC9F0", "#6BCB77", "#F8961E", "#D62828", "#1982C4", "#FFB703"],
                "y_label": "Global Vaccination Coverage (%)",
                "x_label": "Disease",
                "img_title": "Vaccination Coverage for Major Diseases"
            },
            {
                "bar_data": [24.5, 21.3, 18.9, 17.1, 15.6, 14.0, 13.2, 12.5, 11.0, 9.8],
                "bar_labels": ["Obesity", "Smoking", "Alcohol", "Inactivity", "Air Pollution", "High Sugar Intake", "Processed Foods", "Sleep Deprivation", "Stress", "Salt Intake"],
                "bar_colors": ["#FF006E", "#8338EC", "#3A86FF", "#00B4D8", "#FB5607", "#FFD60A", "#A3A847", "#4CAF50", "#D72638", "#6C757D"],
                "y_label": "Associated Risk Score",
                "x_label": "Health Risk Factor",
                "img_title": "Top Lifestyle Risk Factors Impacting Health"
            },
            {
                "bar_data": [12.3, 11.7, 10.9, 10.1, 9.5, 8.8, 8.0, 7.4, 6.8, 6.1],
                "bar_labels": ["Pfizer", "Johnson & Johnson", "Roche", "Merck", "Novartis", "Sanofi", "AbbVie", "GSK", "Bayer", "AstraZeneca"],
                "bar_colors": ["#0077B6", "#0096C7", "#00B4D8", "#90E0EF", "#CAF0F8", "#FFB4A2", "#F28482", "#84A59D", "#F6BD60", "#F7A072"],
                "y_label": "Revenue (Billion USD)",
                "x_label": "Pharmaceutical Company",
                "img_title": "Top 10 Global Pharmaceutical Companies by Revenue"
            },
            {
                "bar_data": [62.4, 59.1, 56.7, 54.2, 52.8, 50.3, 47.9, 45.4, 43.1, 40.7],
                "bar_labels": ["Depression", "Anxiety", "Bipolar Disorder", "Schizophrenia", "PTSD", "OCD", "ADHD", "Autism", "Eating Disorders", "Substance Use"],
                "bar_colors": ["#F94144", "#F3722C", "#F8961E", "#F9C74F", "#90BE6D", "#43AA8B", "#577590", "#277DA1", "#6A0572", "#3F88C5"],
                "y_label": "Prevalence (Millions)",
                "x_label": "Mental Health Condition",
                "img_title": "Global Prevalence of Mental Health Conditions"
            },
            {
                "bar_data": [87.5, 85.2, 83.7, 80.9, 78.6, 75.4, 73.3, 70.1, 68.9, 66.4],
                "bar_labels": ["MRI", "CT Scan", "X-ray", "Ultrasound", "PET Scan", "EEG", "ECG", "Mammography", "DEXA", "Endoscopy"],
                "bar_colors": ["#06D6A0", "#118AB2", "#FFD166", "#EF476F", "#8338EC", "#A3A847", "#00B4D8", "#FB5607", "#FF006E", "#6C757D"],
                "y_label": "Usage Rate (%)",
                "x_label": "Diagnostic Technology",
                "img_title": "Usage Rates of Diagnostic Imaging Technologies"
            },
            {
                "bar_data": [7.6, 7.0, 6.5, 6.1, 5.7, 5.2, 4.8, 4.3, 3.9, 3.5],
                "bar_labels": ["Cardiologists", "Psychiatrists", "Oncologists", "Orthopedists", "Pediatricians", "Radiologists", "Neurologists", "Dermatologists", "Gynecologists", "Urologists"],
                "bar_colors": ["#B5179E", "#3A0CA3", "#4361EE", "#4CC9F0", "#F94144", "#F3722C", "#F8961E", "#90BE6D", "#43AA8B", "#577590"],
                "y_label": "Average Salary (Hundred Thousand USD)",
                "x_label": "Medical Specialty",
                "img_title": "Highest Paid Medical Specialties in the US"
            },
            {
                "bar_data": [98.1, 96.4, 94.7, 93.5, 91.9, 90.2, 88.7, 87.1, 85.6, 84.0],
                "bar_labels": ["Insulin", "Antibiotics", "Antidepressants", "Pain Relievers", "Statins", "Antivirals", "Chemotherapy", "Steroids", "Antihistamines", "Beta Blockers"],
                "bar_colors": ["#F4A261", "#E76F51", "#2A9D8F", "#264653", "#E9C46A", "#D62828", "#A8DADC", "#457B9D", "#E63946", "#1D3557"],
                "y_label": "Prescription Rate (%)",
                "x_label": "Medication Type",
                "img_title": "Most Commonly Prescribed Medication Classes"
            },
            {
                "bar_data": [6.8, 6.2, 5.7, 5.3, 5.0, 4.6, 4.2, 3.9, 3.4, 3.1],
                "bar_labels": ["Cancer Research", "Neuroscience", "Infectious Diseases", "Genetics", "Immunology", "Pharmacology", "Cardiology", "Endocrinology", "Public Health", "Gerontology"],
                "bar_colors": ["#FF6B6B", "#6BCB77", "#4D96FF", "#FFD93D", "#C77DFF", "#00B4D8", "#F9C74F", "#9B5DE5", "#43AA8B", "#3A86FF"],
                "y_label": "Annual Research Funding (Billion USD)",
                "x_label": "Medical Field",
                "img_title": "Top Areas of Medical Research by Funding"
            }
        ],
        "16 - Energy & Environment": [
            {
                "bar_data": [1200, 950, 820, 790, 670, 540, 490, 460, 430, 410],
                "bar_labels": ["China", "USA", "India", "Russia", "Japan", "Germany", "Iran", "South Korea", "Canada", "Brazil"],
                "bar_colors": ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93", "#F3722C", "#4CC9F0", "#3A0CA3", "#E63946", "#2A9D8F"],
                "y_label": "Annual CO₂ Emissions (Million Metric Tons)",
                "x_label": "Country",
                "img_title": "Top 10 CO₂ Emitting Countries"
            },
            {
                "bar_data": [35.2, 32.8, 30.5, 28.7, 27.3, 25.9, 24.4, 22.8, 21.1, 20.0],
                "bar_labels": ["Solar", "Wind", "Hydro", "Geothermal", "Biomass", "Tidal", "Wave", "Waste-to-Energy", "Algae", "Hydrogen"],
                "bar_colors": ["#F72585", "#7209B7", "#3A0CA3", "#4361EE", "#4CC9F0", "#2EC4B6", "#84A59D", "#F28482", "#FFB703", "#90BE6D"],
                "y_label": "Global Investment (Billion USD)",
                "x_label": "Renewable Energy Type",
                "img_title": "Global Investment by Renewable Energy Type"
            },
            {
                "bar_data": [59, 54, 50, 48, 45, 43, 40, 38, 35, 32],
                "bar_labels": ["Paper", "Plastic", "Glass", "Metal", "Electronics", "Textiles", "Food Waste", "Batteries", "Wood", "Rubber"],
                "bar_colors": ["#118AB2", "#06D6A0", "#FFD166", "#EF476F", "#F9C74F", "#90BE6D", "#F3722C", "#6A0572", "#1D3557", "#3F88C5"],
                "y_label": "Recycling Rate (%)",
                "x_label": "Material",
                "img_title": "Recycling Rates by Material Type"
            },
            {
                "bar_data": [22.1, 20.8, 19.7, 18.6, 17.4, 16.3, 15.2, 14.1, 13.0, 12.0],
                "bar_labels": ["China", "USA", "Germany", "India", "Japan", "Brazil", "Canada", "UK", "France", "Spain"],
                "bar_colors": ["#E63946", "#F1FAEE", "#A8DADC", "#457B9D", "#1D3557", "#F77F00", "#F4A261", "#2A9D8F", "#FF6B6B", "#6A4C93"],
                "y_label": "Renewable Energy Production (Exajoules)",
                "x_label": "Country",
                "img_title": "Top Renewable Energy Producers (2025)"
            },
            {
                "bar_data": [50.3, 47.2, 45.5, 42.0, 40.1, 38.7, 36.4, 34.6, 32.5, 30.2],
                "bar_labels": ["Beijing", "Delhi", "Lahore", "Dhaka", "Ulaanbaatar", "Jakarta", "Cairo", "Mumbai", "Tehran", "Baghdad"],
                "bar_colors": ["#FF006E", "#8338EC", "#3A86FF", "#00B4D8", "#FB5607", "#FFD60A", "#A3A847", "#4CAF50", "#D72638", "#6C757D"],
                "y_label": "PM2.5 Air Pollution (µg/m³)",
                "x_label": "City",
                "img_title": "Most Polluted Cities by PM2.5 Concentration"
            },
            {
                "bar_data": [14.2, 13.7, 13.1, 12.5, 12.0, 11.4, 10.9, 10.2, 9.8, 9.2],
                "bar_labels": ["Amazon", "Congo", "New Guinea", "Valdivian", "Kinabalu", "Sundaland", "Atlantic Forest", "Indo-Burma", "Himalaya", "Western Ghats"],
                "bar_colors": ["#F94144", "#F3722C", "#F8961E", "#F9C74F", "#90BE6D", "#43AA8B", "#577590", "#277DA1", "#3A0CA3", "#7209B7"],
                "y_label": "Biodiversity Score",
                "x_label": "Rainforest Region",
                "img_title": "Rainforest Regions by Biodiversity Index"
            },
            {
                "bar_data": [98.1, 94.7, 91.2, 89.0, 87.5, 84.9, 82.6, 80.1, 78.3, 75.9],
                "bar_labels": ["Refrigerators", "AC Units", "Lighting", "Washing Machines", "Dishwashers", "Dryers", "Microwaves", "Heaters", "TVs", "Computers"],
                "bar_colors": ["#F4A261", "#2A9D8F", "#E76F51", "#264653", "#E9C46A", "#A8DADC", "#D62828", "#A3A847", "#3A86FF", "#1D3557"],
                "y_label": "Energy Efficiency Score (%)",
                "x_label": "Appliance",
                "img_title": "Household Appliances by Energy Efficiency"
            },
            {
                "bar_data": [230, 210, 190, 180, 160, 150, 140, 130, 120, 110],
                "bar_labels": ["Texas", "California", "Iowa", "Oklahoma", "Kansas", "Illinois", "Minnesota", "Colorado", "New York", "New Mexico"],
                "bar_colors": ["#EF476F", "#FFD166", "#06D6A0", "#118AB2", "#073B4C", "#F72585", "#7209B7", "#3A0CA3", "#4361EE", "#4CC9F0"],
                "y_label": "Wind Power Capacity (GW)",
                "x_label": "US State",
                "img_title": "Top US States by Wind Power Capacity"
            },
            {
                "bar_data": [89, 85, 82, 79, 75, 72, 69, 66, 63, 60],
                "bar_labels": ["Hydropower", "Wind", "Solar", "Geothermal", "Biomass", "Nuclear", "Natural Gas", "Oil", "Coal", "Peat"],
                "bar_colors": ["#FFB703", "#FB8500", "#023047", "#8ECAE6", "#219EBC", "#FF006E", "#8338EC", "#3A86FF", "#06D6A0", "#EF476F"],
                "y_label": "Sustainability Score (Out of 100)",
                "x_label": "Energy Source",
                "img_title": "Energy Sources Ranked by Sustainability"
            },
            {
                "bar_data": [18.5, 17.0, 16.3, 15.8, 15.0, 14.2, 13.7, 13.1, 12.4, 11.8],
                "bar_labels": ["Maldives", "Tuvalu", "Kiribati", "Marshall Islands", "Bangladesh", "Vanuatu", "Solomon Islands", "Seychelles", "Micronesia", "Palau"],
                "bar_colors": ["#00B4D8", "#0077B6", "#90E0EF", "#CAF0F8", "#E63946", "#FF6B6B", "#A3A847", "#F8961E", "#264653", "#457B9D"],
                "y_label": "Sea Level Rise Risk Index",
                "x_label": "Country",
                "img_title": "Nations Most at Risk from Sea Level Rise"
            }
        ],
        "17 - Travel & Expedition": [
            {
                "bar_data": [91.2, 89.4, 86.3, 85.7, 84.1, 82.3, 80.6, 79.5, 77.8, 75.9],
                "bar_labels": ["France", "Spain", "USA", "China", "Italy", "Turkey", "Mexico", "Thailand", "Germany", "UK"],
                "bar_colors": ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93", "#F3722C", "#4CC9F0", "#3A0CA3", "#E63946", "#2A9D8F"],
                "y_label": "Annual Tourists (Millions)",
                "x_label": "Country",
                "img_title": "Most Visited Countries by International Tourists"
            },
            {
                "bar_data": [22.4, 19.8, 18.7, 17.9, 16.5, 15.3, 14.8, 13.2, 12.9, 11.7],
                "bar_labels": ["Bangkok", "Paris", "London", "Dubai", "Istanbul", "New York", "Kuala Lumpur", "Tokyo", "Rome", "Barcelona"],
                "bar_colors": ["#F72585", "#7209B7", "#3A0CA3", "#4361EE", "#4CC9F0", "#2EC4B6", "#84A59D", "#F28482", "#FFB703", "#90BE6D"],
                "y_label": "Annual Visitors (Millions)",
                "x_label": "City",
                "img_title": "Top Tourist Cities by Annual Visitors"
            },
            {
                "bar_data": [19, 17, 15, 14, 13, 11, 10, 9, 8, 7],
                "bar_labels": ["Everest", "K2", "Kilimanjaro", "Aconcagua", "Denali", "Elbrus", "Vinson", "Matterhorn", "Mont Blanc", "Fuji"],
                "bar_colors": ["#E63946", "#F1FAEE", "#A8DADC", "#457B9D", "#1D3557", "#F77F00", "#F4A261", "#2A9D8F", "#FF6B6B", "#6A4C93"],
                "y_label": "Annual Climbers (Thousands)",
                "x_label": "Mountain",
                "img_title": "Popular Mountains for Expedition Climbing"
            },
            {
                "bar_data": [18.3, 17.2, 16.1, 15.0, 14.3, 13.5, 12.7, 12.0, 11.5, 10.6],
                "bar_labels": ["Norway", "Switzerland", "New Zealand", "Canada", "Iceland", "Japan", "Scotland", "Austria", "Chile", "USA"],
                "bar_colors": ["#FB5607", "#FF006E", "#8338EC", "#3A86FF", "#06D6A0", "#EF476F", "#FFB703", "#219EBC", "#F9C74F", "#118AB2"],
                "y_label": "Adventure Travel Index",
                "x_label": "Country",
                "img_title": "Top Countries for Adventure Travel"
            },
            {
                "bar_data": [4.5, 4.2, 4.0, 3.8, 3.5, 3.3, 3.1, 2.8, 2.6, 2.4],
                "bar_labels": ["Interrail", "Eurail", "JR Pass", "Amtrak USA Rail", "BritRail", "Swiss Travel Pass", "Deutsche Bahn", "TGV France", "Via Rail Canada", "Renfe Spain"],
                "bar_colors": ["#EF476F", "#FFD166", "#06D6A0", "#118AB2", "#073B4C", "#F72585", "#7209B7", "#3A0CA3", "#4361EE", "#4CC9F0"],
                "y_label": "Annual Users (Millions)",
                "x_label": "Rail Travel Program",
                "img_title": "Popular Rail Pass Programs Globally"
            },
            {
                "bar_data": [92, 88, 84, 81, 78, 76, 73, 70, 67, 65],
                "bar_labels": ["TripAdvisor", "Booking.com", "Expedia", "Airbnb", "Skyscanner", "Kayak", "Agoda", "Hostelworld", "Couchsurfing", "Trivago"],
                "bar_colors": ["#F94144", "#F3722C", "#F8961E", "#F9C74F", "#90BE6D", "#43AA8B", "#577590", "#277DA1", "#3A0CA3", "#7209B7"],
                "y_label": "User Trust Score",
                "x_label": "Travel Platform",
                "img_title": "Most Trusted Online Travel Platforms"
            },
            {
                "bar_data": [15.2, 14.8, 13.9, 13.2, 12.7, 12.1, 11.6, 11.0, 10.4, 10.0],
                "bar_labels": ["Indonesia", "India", "Philippines", "Brazil", "Mexico", "Peru", "Thailand", "Morocco", "Nepal", "Colombia"],
                "bar_colors": ["#E9C46A", "#2A9D8F", "#E76F51", "#264653", "#F4A261", "#A8DADC", "#D62828", "#A3A847", "#3A86FF", "#1D3557"],
                "y_label": "Eco-Tourism Growth (%)",
                "x_label": "Country",
                "img_title": "Countries with Fastest Growing Eco-Tourism"
            },
            {
                "bar_data": [1200, 980, 900, 870, 820, 790, 750, 710, 680, 650],
                "bar_labels": ["Schengen Visa", "US Visa", "UK Visa", "Canada Visa", "Australia Visa", "Japan Visa", "China Visa", "India Visa", "Turkey Visa", "Brazil Visa"],
                "bar_colors": ["#F3722C", "#FF6B6B", "#F9C74F", "#43AA8B", "#577590", "#7209B7", "#3A0CA3", "#8AC926", "#FFB703", "#4361EE"],
                "y_label": "Visa Applications (Thousands)",
                "x_label": "Visa Type",
                "img_title": "Most Applied Tourist Visas Globally"
            },
            {
                "bar_data": [23.4, 21.8, 20.5, 19.3, 18.7, 17.1, 16.4, 15.0, 14.3, 13.5],
                "bar_labels": ["Santorini", "Bali", "Maui", "Maldives", "Ibiza", "Phuket", "Mykonos", "Bora Bora", "Seychelles", "Capri"],
                "bar_colors": ["#00B4D8", "#0077B6", "#90E0EF", "#CAF0F8", "#E63946", "#FF6B6B", "#A3A847", "#F8961E", "#264653", "#457B9D"],
                "y_label": "Instagram Mentions (Millions)",
                "x_label": "Island",
                "img_title": "Most Instagrammed Travel Islands"
            },
            {
                "bar_data": [7.4, 6.9, 6.3, 5.8, 5.4, 5.0, 4.6, 4.3, 4.0, 3.7],
                "bar_labels": ["Camino de Santiago", "Inca Trail", "Appalachian Trail", "PCT", "Great Ocean Walk", "Torres del Paine", "West Highland Way", "Annapurna Circuit", "Overland Track", "Lycian Way"],
                "bar_colors": ["#F72585", "#3A0CA3", "#4361EE", "#4CC9F0", "#2EC4B6", "#84A59D", "#F28482", "#FFB703", "#90BE6D", "#EF476F"],
                "y_label": "Annual Trekkers (Hundreds of Thousands)",
                "x_label": "Trail",
                "img_title": "Most Popular Trekking Trails Worldwide"
            }
        ],
        "18 - Arts & Culture": [
            {
                "bar_data": [9.3, 8.8, 8.5, 8.2, 7.9, 7.4, 7.1, 6.7, 6.4, 6.1],
                "bar_labels": ["Louvre", "British Museum", "Vatican Museums", "Metropolitan Museum", "Uffizi Gallery", "Hermitage", "Rijksmuseum", "Museo del Prado", "Tate Modern", "Getty Center"],
                "bar_colors": ["#E63946", "#F1FAEE", "#A8DADC", "#457B9D", "#1D3557", "#F77F00", "#F4A261", "#2A9D8F", "#FF6B6B", "#6A4C93"],
                "y_label": "Annual Visitors (Millions)",
                "x_label": "Museum",
                "img_title": "Most Visited Art Museums Worldwide"
            },
            {
                "bar_data": [230, 215, 204, 190, 180, 172, 160, 154, 146, 139],
                "bar_labels": ["Mona Lisa", "Starry Night", "The Scream", "Girl with a Pearl Earring", "The Last Supper", "Guernica", "The Kiss", "The Birth of Venus", "American Gothic", "The Persistence of Memory"],
                "bar_colors": ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93", "#F3722C", "#4CC9F0", "#3A0CA3", "#E63946", "#2A9D8F"],
                "y_label": "Annual Mentions (Thousands)",
                "x_label": "Artwork",
                "img_title": "Most Referenced Paintings in Pop Culture"
            },
            {
                "bar_data": [12.4, 11.7, 11.1, 10.5, 9.8, 9.3, 8.9, 8.3, 7.8, 7.1],
                "bar_labels": ["Vienna", "Paris", "New York", "Milan", "Berlin", "Barcelona", "Florence", "London", "Amsterdam", "Tokyo"],
                "bar_colors": ["#F72585", "#7209B7", "#3A0CA3", "#4361EE", "#4CC9F0", "#2EC4B6", "#84A59D", "#F28482", "#FFB703", "#90BE6D"],
                "y_label": "Cultural Events per Year (Thousands)",
                "x_label": "City",
                "img_title": "Cities Hosting the Most Cultural Events Annually"
            },
            {
                "bar_data": [320, 300, 285, 270, 260, 248, 230, 222, 215, 210],
                "bar_labels": ["Mexico", "India", "China", "Japan", "Italy", "France", "Brazil", "Greece", "Turkey", "Iran"],
                "bar_colors": ["#FB5607", "#FF006E", "#8338EC", "#3A86FF", "#06D6A0", "#EF476F", "#FFB703", "#219EBC", "#F9C74F", "#118AB2"],
                "y_label": "UNESCO Sites",
                "x_label": "Country",
                "img_title": "Countries with the Most UNESCO Cultural Heritage Sites"
            },
            {
                "bar_data": [1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.85, 0.82, 0.8, 0.75],
                "bar_labels": ["Coachella", "Glastonbury", "Burning Man", "Tomorrowland", "Lollapalooza", "SXSW", "Montreux Jazz", "Venice Biennale", "Edinburgh Fringe", "La Tomatina"],
                "bar_colors": ["#F94144", "#F3722C", "#F8961E", "#F9C74F", "#90BE6D", "#43AA8B", "#577590", "#277DA1", "#3A0CA3", "#7209B7"],
                "y_label": "Annual Attendees (Millions)",
                "x_label": "Festival",
                "img_title": "Major Arts and Culture Festivals by Attendance"
            },
            {
                "bar_data": [800, 760, 710, 680, 645, 610, 580, 540, 520, 490],
                "bar_labels": ["New York Philharmonic", "Berlin Philharmonic", "London Symphony", "Vienna Philharmonic", "Chicago Symphony", "Cleveland Orchestra", "Boston Symphony", "LA Philharmonic", "Amsterdam Concertgebouw", "San Francisco Symphony"],
                "bar_colors": ["#E76F51", "#2A9D8F", "#264653", "#F4A261", "#A8DADC", "#D62828", "#A3A847", "#3A86FF", "#1D3557", "#F72585"],
                "y_label": "Annual Performances",
                "x_label": "Orchestra",
                "img_title": "Top Performing Symphony Orchestras by Annual Concerts"
            },
            {
                "bar_data": [18.5, 17.6, 16.9, 15.8, 15.0, 14.2, 13.5, 12.8, 12.0, 11.3],
                "bar_labels": ["Broadway", "West End", "Chicago Theatre", "Sydney Opera House", "Toronto Theatre District", "Berlin Theatre", "Paris Opera", "Mumbai NCPA", "Tokyo Kabuki", "Moscow Bolshoi"],
                "bar_colors": ["#F72585", "#3A0CA3", "#4361EE", "#4CC9F0", "#2EC4B6", "#84A59D", "#F28482", "#FFB703", "#90BE6D", "#EF476F"],
                "y_label": "Annual Productions",
                "x_label": "Theatre District",
                "img_title": "Global Theatre Hubs by Annual Productions"
            },
            {
                "bar_data": [540, 520, 490, 470, 455, 430, 415, 400, 385, 370],
                "bar_labels": ["USA", "India", "France", "Japan", "Italy", "Russia", "Germany", "UK", "China", "South Korea"],
                "bar_colors": ["#FF6B6B", "#F3722C", "#F9C74F", "#43AA8B", "#577590", "#7209B7", "#3A0CA3", "#8AC926", "#FFB703", "#4361EE"],
                "y_label": "Cultural Institutions Funded",
                "x_label": "Country",
                "img_title": "Countries with Most Funded Cultural Institutions"
            },
            {
                "bar_data": [30, 28, 26, 25, 24, 22, 21, 20, 19, 18],
                "bar_labels": ["Calligraphy", "Weaving", "Pottery", "Mask Making", "Wood Carving", "Batiking", "Glass Blowing", "Origami", "Mosaic Art", "Papercutting"],
                "bar_colors": ["#EF476F", "#FFD166", "#06D6A0", "#118AB2", "#073B4C", "#F72585", "#7209B7", "#3A0CA3", "#4361EE", "#4CC9F0"],
                "y_label": "Global Craft Recognition Score",
                "x_label": "Art Form",
                "img_title": "Traditional Arts with Highest Global Recognition"
            },
            {
                "bar_data": [17.2, 16.4, 15.7, 15.0, 14.6, 14.0, 13.4, 12.9, 12.3, 11.8],
                "bar_labels": ["Tango (Argentina)", "Flamenco (Spain)", "Bharatanatyam (India)", "Ballet (France/Russia)", "Hula (Hawaii)", "Kathak (India)", "Kabuki (Japan)", "Cossack Dance (Ukraine)", "Polka (Czech)", "Whirling Dervishes (Turkey)"],
                "bar_colors": ["#00B4D8", "#0077B6", "#90E0EF", "#CAF0F8", "#E63946", "#FF6B6B", "#A3A847", "#F8961E", "#264653", "#457B9D"],
                "y_label": "UNESCO Intangible Heritage Score",
                "x_label": "Dance Form",
                "img_title": "Traditional Dances Recognized as Cultural Heritage"
            }
        ],
        "19 - Communication & Collaboration": [
            {
                "bar_data": [97.5, 95.1, 92.4, 90.7, 88.2, 85.6, 83.9, 81.3, 78.8, 76.5],
                "bar_labels": ["Email", "Instant Messaging", "Video Calls", "Voice Calls", "Collaborative Docs", "Project Management Tools", "Intranet", "Cloud Storage", "Forums", "Wikis"],
                "bar_colors": ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51", "#A8DADC", "#457B9D", "#1D3557", "#F72585", "#7209B7"],
                "y_label": "Usage in Workplaces (%)",
                "x_label": "Communication Tools",
                "img_title": "Most Used Communication Tools in Corporate Settings"
            },
            {
                "bar_data": [81, 78, 75, 72, 70, 68, 65, 63, 60, 58],
                "bar_labels": ["Slack", "Microsoft Teams", "Zoom", "Google Meet", "Skype", "Discord", "Webex", "Mattermost", "Rocket.Chat", "Chanty"],
                "bar_colors": ["#3A86FF", "#8338EC", "#FF006E", "#FB5607", "#FFBE0B", "#8AC926", "#1982C4", "#6A4C93", "#EF476F", "#06D6A0"],
                "y_label": "Market Adoption Rate (%)",
                "x_label": "Collaboration Platforms",
                "img_title": "Adoption Rates of Popular Collaboration Platforms"
            },
            {
                "bar_data": [95, 89, 84, 79, 76, 72, 70, 66, 62, 59],
                "bar_labels": ["Face-to-Face", "Phone", "Email", "Instant Messaging", "Social Media", "Video Conferencing", "Text Messages", "Memos", "Bulletin Boards", "Surveys"],
                "bar_colors": ["#F94144", "#F3722C", "#F8961E", "#F9C74F", "#90BE6D", "#43AA8B", "#577590", "#277DA1", "#4CC9F0", "#7209B7"],
                "y_label": "Effectiveness Rating (%)",
                "x_label": "Communication Methods",
                "img_title": "Perceived Effectiveness of Workplace Communication Methods"
            },
            {
                "bar_data": [240, 230, 220, 215, 208, 200, 192, 185, 178, 170],
                "bar_labels": ["USA", "India", "China", "UK", "Germany", "Canada", "Australia", "France", "Japan", "Brazil"],
                "bar_colors": ["#D62828", "#F77F00", "#FCBF49", "#EAE2B7", "#A8DADC", "#457B9D", "#2A9D8F", "#1D3557", "#F72585", "#7209B7"],
                "y_label": "Daily Online Meetings (Millions)",
                "x_label": "Country",
                "img_title": "Countries with the Highest Volume of Online Meetings"
            },
            {
                "bar_data": [92, 89, 85, 82, 79, 76, 73, 70, 67, 63],
                "bar_labels": ["Clarity", "Tone", "Empathy", "Conciseness", "Body Language", "Confidence", "Listening", "Timing", "Feedback", "Consistency"],
                "bar_colors": ["#3A0CA3", "#4361EE", "#4CC9F0", "#F72585", "#7209B7", "#B5179E", "#F77F00", "#FFBA08", "#43AA8B", "#577590"],
                "y_label": "Importance Score (%)",
                "x_label": "Communication Traits",
                "img_title": "Most Valued Communication Traits in Team Environments"
            },
            {
                "bar_data": [88, 85, 81, 78, 75, 71, 69, 66, 64, 61],
                "bar_labels": ["Task Updates", "Project Goals", "Deadlines", "Feedback Sharing", "Meeting Notes", "Brainstorming", "Knowledge Sharing", "Conflict Resolution", "Recognition", "Social Interaction"],
                "bar_colors": ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93", "#E63946", "#F3722C", "#F8961E", "#43AA8B", "#577590"],
                "y_label": "Communication Frequency (%)",
                "x_label": "Topics in Teams",
                "img_title": "Most Frequently Communicated Topics in Teams"
            },
            {
                "bar_data": [39, 37, 35, 34, 32, 30, 29, 27, 25, 24],
                "bar_labels": ["Email Overload", "Time Zones", "Misinterpretation", "Tool Fatigue", "Lack of Engagement", "Delayed Responses", "Too Many Meetings", "Language Barriers", "Technical Glitches", "Distractions"],
                "bar_colors": ["#EF476F", "#FFD166", "#06D6A0", "#118AB2", "#073B4C", "#F72585", "#7209B7", "#3A0CA3", "#4361EE", "#4CC9F0"],
                "y_label": "Reported Incidence Rate (%)",
                "x_label": "Communication Challenge",
                "img_title": "Top Communication Challenges in Remote Teams"
            },
            {
                "bar_data": [120, 110, 105, 95, 90, 87, 82, 78, 74, 70],
                "bar_labels": ["GitHub", "Trello", "Notion", "Jira", "Slack", "Confluence", "ClickUp", "Asana", "Basecamp", "Monday.com"],
                "bar_colors": ["#219EBC", "#023047", "#FFB703", "#FB8500", "#8ECAE6", "#F94144", "#F3722C", "#90BE6D", "#577590", "#FF6B6B"],
                "y_label": "Average Weekly Interactions (Thousands)",
                "x_label": "Platform",
                "img_title": "Most Used Collaboration Platforms by Developer Teams"
            },
            {
                "bar_data": [65, 63, 60, 58, 55, 52, 50, 47, 45, 42],
                "bar_labels": ["1-on-1s", "Team Standups", "All-Hands", "Check-ins", "Workshops", "Sync Meetings", "Townhalls", "Retrospectives", "Daily Scrums", "Coffee Chats"],
                "bar_colors": ["#7209B7", "#3A0CA3", "#F72585", "#4CC9F0", "#F8961E", "#1982C4", "#06D6A0", "#F9C74F", "#FF006E", "#8338EC"],
                "y_label": "Common Usage in Teams (%)",
                "x_label": "Meeting Types",
                "img_title": "Most Common Types of Team Meetings"
            },
            {
                "bar_data": [91, 88, 84, 80, 77, 73, 70, 67, 63, 60],
                "bar_labels": ["Respect", "Trust", "Openness", "Accountability", "Shared Goals", "Active Listening", "Constructive Feedback", "Empathy", "Inclusion", "Consistency"],
                "bar_colors": ["#00B4D8", "#0077B6", "#90E0EF", "#CAF0F8", "#E63946", "#FF6B6B", "#A3A847", "#F8961E", "#264653", "#457B9D"],
                "y_label": "Team Success Contribution (%)",
                "x_label": "Collaborative Values",
                "img_title": "Top Values That Drive Effective Team Collaboration"
            }
        ],
        "20 - Language & Linguistics": [
            {
                "bar_data": [49.37, 99.03, 27.17, 35.9, 51.62, 30.21, 54.37, 22.36, 59.63, 86.1, 45.24, 11.15, 31.01, 67.45],
                "bar_labels": ["Sociolinguistics", "Phonology", "Lexicography", "Semantics", "Neurolinguistics", "Graphemics", "Morphology", "Computational Linguistics", "Applied Linguistics", "Etymology", "Syntax", "Language Typology", "Pragmatics", "Psycholinguistics"],
                "bar_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4", "#AA6E28", "#FF7F50", "#6495ED", "#FF69B4"],
                "y_label": "Research Focus Score",
                "x_label": "Items",
                "img_title": "Language & Linguistics Analysis #1",
            },
            {
                "bar_data": [95.2, 51.45, 33.84, 39.42, 93.06, 19.91, 74.99, 89.42, 66.02, 74.79, 43.02, 78.62, 88.5, 98.69],
                "bar_labels": ["Phonology", "Dialectology", "Phonetics", "Computational Linguistics", "Lexicography", "Language Typology", "Semantics", "Historical Linguistics", "Discourse Analysis", "Neurolinguistics", "Syntax", "Applied Linguistics", "Graphemics", "Psycholinguistics"],
                "bar_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4", "#AA6E28", "#FF7F50", "#6495ED", "#FF69B4"],
                "y_label": "Research Focus Score",
                "x_label": "Items",
                "img_title": "Language & Linguistics Analysis #2",
            },
            {
                "bar_data": [78.32, 26.44, 83.11, 65.28, 92.41, 56.34, 41.92, 37.82, 29.61, 48.76, 19.04, 84.33],
                "bar_labels": ["Morphology", "Lexicography", "Syntax", "Phonetics", "Discourse Analysis", "Psycholinguistics", "Language Acquisition", "Semantics", "Sociolinguistics", "Etymology", "Graphemics", "Historical Linguistics"],
                "bar_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4", "#AA6E28", "#FF7F50"],
                "y_label": "Research Focus Score",
                "x_label": "Items",
                "img_title": "Language & Linguistics Analysis #3",
            },
            {
                "bar_data": [61.27, 76.48, 89.76, 34.51, 50.69, 24.87, 11.26, 93.33, 82.79, 64.5, 58.92],
                "bar_labels": ["Language Typology", "Syntax", "Graphemics", "Semantics", "Applied Linguistics", "Computational Linguistics", "Etymology", "Psycholinguistics", "Sociolinguistics", "Pragmatics", "Phonology"],
                "bar_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4", "#AA6E28"],
                "y_label": "Research Focus Score",
                "x_label": "Items",
                "img_title": "Language & Linguistics Analysis #4",
            },
            {
                "bar_data": [87.62, 39.44, 72.15, 90.74, 25.69, 58.96, 32.56, 67.82, 44.13, 74.21],
                "bar_labels": ["Psycholinguistics", "Historical Linguistics", "Phonetics", "Semantics", "Morphology", "Computational Linguistics", "Discourse Analysis", "Language Typology", "Graphemics", "Syntax"],
                "bar_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4"],
                "y_label": "Research Focus Score",
                "x_label": "Items",
                "img_title": "Language & Linguistics Analysis #5",
            },
            {
                "bar_data": [43.88, 59.75, 26.3, 96.12, 37.44, 88.29, 84.01, 45.78, 49.91, 69.72, 93.81],
                "bar_labels": ["Phonology", "Lexicography", "Graphemics", "Pragmatics", "Morphology", "Syntax", "Neurolinguistics", "Applied Linguistics", "Computational Linguistics", "Phonetics", "Discourse Analysis"],
                "bar_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4", "#AA6E28"],
                "y_label": "Research Focus Score",
                "x_label": "Items",
                "img_title": "Language & Linguistics Analysis #6",
            },
            {
                "bar_data": [58.55, 72.61, 99.33, 47.12, 88.74, 24.91, 33.67, 36.82, 91.09, 53.5, 84.2, 44.66],
                "bar_labels": ["Syntax", "Pragmatics", "Lexicography", "Phonology", "Phonetics", "Sociolinguistics", "Historical Linguistics", "Language Acquisition", "Computational Linguistics", "Graphemics", "Discourse Analysis", "Etymology"],
                "bar_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4", "#AA6E28", "#FF7F50"],
                "y_label": "Research Focus Score",
                "x_label": "Items",
                "img_title": "Language & Linguistics Analysis #7",
            },
            {
                "bar_data": [89.56, 67.21, 73.18, 64.19, 59.87, 42.66, 21.73, 31.91, 39.87, 51.0],
                "bar_labels": ["Graphemics", "Semantics", "Sociolinguistics", "Discourse Analysis", "Syntax", "Computational Linguistics", "Morphology", "Language Acquisition", "Phonology", "Historical Linguistics"],
                "bar_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4"],
                "y_label": "Research Focus Score",
                "x_label": "Items",
                "img_title": "Language & Linguistics Analysis #8",
            },
            {
                "bar_data": [22.6, 28.41, 97.91, 76.23, 47.51, 88.38, 42.6, 94.79, 85.91, 37.18],
                "bar_labels": ["Semantics", "Etymology", "Applied Linguistics", "Syntax", "Discourse Analysis", "Lexicography", "Language Typology", "Phonetics", "Pragmatics", "Morphology"],
                "bar_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4"],
                "y_label": "Research Focus Score",
                "x_label": "Items",
                "img_title": "Language & Linguistics Analysis #9",
            },
            {
                "bar_data": [41.99, 35.88, 29.67, 61.18, 72.99, 53.91, 90.61, 64.88, 48.24, 56.31],
                "bar_labels": ["Phonology", "Syntax", "Morphology", "Lexicography", "Neurolinguistics", "Language Typology", "Discourse Analysis", "Semantics", "Computational Linguistics", "Pragmatics"],
                "bar_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4"],
                "y_label": "Research Focus Score",
                "x_label": "Items",
                "img_title": "Language & Linguistics Analysis #10",
            }
        ],
        "21 - History & Archaeology": [
            {
                "bar_data": [71.38, 95.33, 99.39, 97.56, 61.83, 37.06, 52.6, 54.52, 47.05, 98.6, 36.33, 61.59],
                "bar_labels": ["Ancient Civilizations", "Historical Figures", "Renaissance", "Military History",
                            "Industrial Revolution", "Medieval Europe", "World Wars", "Artifacts",
                            "Colonial History", "Cultural Heritage", "Prehistoric Era", "Archaeological Sites"],
                "bar_colors": ["#AA6E28", "#C02222", "#BF7023", "#2279E4", "#EEA658", "#73ECE2", "#92D610",
                            "#ADCDF6", "#FFF46F", "#9370DB", "#6495ED", "#3DB60D"],
                "y_label": "Research Significance Score",
                "x_label": "Historical Topics",
                "img_title": "History & Archaeology Insights #1"
            },
            {
                "bar_data": [56.65, 41.6, 59.88, 55.44, 97.19, 50.19, 61.7, 88.16, 94.41, 51.29],
                "bar_labels": ["Religious Movements", "Modern History", "Archaeological Sites", "Prehistoric Era",
                            "Renaissance", "Medieval Europe", "Exploration History", "Historical Figures",
                            "Colonial History", "World Wars"],
                "bar_colors": ["#EEA658", "#92D610", "#ADCDF6", "#C02222", "#DE7676", "#73ECE2", "#FF69B4",
                            "#6495ED", "#3DB60D", "#FF7F50"],
                "y_label": "Research Significance Score",
                "x_label": "Historical Topics",
                "img_title": "History & Archaeology Insights #2"
            },
            {
                "bar_data": [21.26, 94.11, 97.62, 63.17, 69.18, 28.16, 25.25, 55.81, 75.82, 66.72, 56.31, 26.63, 64.21, 41.0],
                "bar_labels": ["Modern History", "Cultural Heritage", "World Wars", "Prehistoric Era", "Religious Movements",
                            "Archaeological Sites", "Renaissance", "Artifacts", "Military History", "Ancient Civilizations",
                            "Historical Figures", "Industrial Revolution", "Exploration History", "Medieval Europe"],
                "bar_colors": ["#92D610", "#6495ED", "#ADCDF6", "#BF7023", "#73ECE2", "#DE7676", "#C02222",
                            "#AA6E28", "#FF7F50", "#2279E4", "#FFF46F", "#EEA658", "#9370DB", "#3DB60D"],
                "y_label": "Research Significance Score",
                "x_label": "Historical Topics",
                "img_title": "History & Archaeology Insights #3"
            },
            {
                "bar_data": [89.85, 23.12, 49.96, 30.83, 67.88, 67.6, 34.24, 39.24, 21.36, 96.86],
                "bar_labels": ["Industrial Revolution", "Renaissance", "Medieval Europe", "Archaeological Sites",
                            "Colonial History", "Prehistoric Era", "Religious Movements", "Exploration History",
                            "Cultural Heritage", "Artifacts"],
                "bar_colors": ["#73ECE2", "#FF69B4", "#92D610", "#ADCDF6", "#BF7023", "#3DB60D", "#6495ED",
                            "#FFF46F", "#DE7676", "#EEA658"],
                "y_label": "Research Significance Score",
                "x_label": "Historical Topics",
                "img_title": "History & Archaeology Insights #4"
            },
            {
                "bar_data": [98.9, 72.73, 20.48, 84.62, 31.02, 60.3, 52.42, 22.22, 57.74, 68.94, 53.27, 30.77],
                "bar_labels": ["Military History", "Prehistoric Era", "Historical Figures", "Industrial Revolution",
                            "Artifacts", "Modern History", "World Wars", "Ancient Civilizations",
                            "Religious Movements", "Colonial History", "Archaeological Sites", "Exploration History"],
                "bar_colors": ["#ADCDF6", "#C02222", "#6495ED", "#3DB60D", "#9370DB", "#FFF46F", "#EEA658",
                            "#DE7676", "#AA6E28", "#92D610", "#73ECE2", "#BF7023"],
                "y_label": "Research Significance Score",
                "x_label": "Historical Topics",
                "img_title": "History & Archaeology Insights #5"
            },
            {
                "bar_data": [24.26, 71.93, 29.72, 36.39, 77.65, 49.71, 54.3, 74.92, 29.44, 72.13],
                "bar_labels": ["Exploration History", "Medieval Europe", "Historical Figures", "Renaissance",
                            "World Wars", "Industrial Revolution", "Cultural Heritage", "Modern History",
                            "Colonial History", "Religious Movements"],
                "bar_colors": ["#FFF46F", "#BF7023", "#ADCDF6", "#C02222", "#FF69B4", "#3DB60D", "#AA6E28",
                            "#92D610", "#EEA658", "#DE7676"],
                "y_label": "Research Significance Score",
                "x_label": "Historical Topics",
                "img_title": "History & Archaeology Insights #6"
            },
            {
                "bar_data": [24.48, 79.22, 64.51, 79.93, 23.61, 76.5, 21.65, 41.09, 68.72, 37.72, 44.32, 34.5, 42.06],
                "bar_labels": ["Historical Figures", "World Wars", "Renaissance", "Artifacts", "Exploration History",
                            "Religious Movements", "Archaeological Sites", "Industrial Revolution", "Military History",
                            "Colonial History", "Prehistoric Era", "Ancient Civilizations", "Cultural Heritage"],
                "bar_colors": ["#FF69B4", "#3DB60D", "#9370DB", "#92D610", "#6495ED", "#DE7676", "#EEA658",
                            "#2279E4", "#FFF46F", "#C02222", "#73ECE2", "#FF7F50", "#AA6E28"],
                "y_label": "Research Significance Score",
                "x_label": "Historical Topics",
                "img_title": "History & Archaeology Insights #7"
            },
            {
                "bar_data": [21.38, 21.28, 21.46, 62.75, 87.23, 92.66, 76.36, 79.09, 24.43, 60.25, 51.93, 76.77, 66.49],
                "bar_labels": ["Military History", "Religious Movements", "Renaissance", "Colonial History",
                            "World Wars", "Archaeological Sites", "Medieval Europe", "Cultural Heritage",
                            "Exploration History", "Ancient Civilizations", "Modern History",
                            "Industrial Revolution", "Artifacts"],
                "bar_colors": ["#AA6E28", "#FF69B4", "#FF7F50", "#EEA658", "#6495ED", "#C02222", "#FFF46F",
                            "#9370DB", "#92D610", "#73ECE2", "#3DB60D", "#2279E4", "#BF7023"],
                "y_label": "Research Significance Score",
                "x_label": "Historical Topics",
                "img_title": "History & Archaeology Insights #8"
            },
            {
                "bar_data": [40.43, 83.75, 50.76, 67.82, 22.62, 35.73, 98.85, 69.23, 99.81, 41.52, 41.19, 54.23],
                "bar_labels": ["Cultural Heritage", "Exploration History", "Medieval Europe", "Ancient Civilizations",
                            "Artifacts", "Archaeological Sites", "World Wars", "Historical Figures",
                            "Religious Movements", "Military History", "Modern History", "Colonial History"],
                "bar_colors": ["#AA6E28", "#BF7023", "#FF7F50", "#EEA658", "#FFF46F", "#3DB60D", "#6495ED",
                            "#DE7676", "#9370DB", "#ADCDF6", "#73ECE2", "#2279E4"],
                "y_label": "Research Significance Score",
                "x_label": "Historical Topics",
                "img_title": "History & Archaeology Insights #9"
            },
            {
                "bar_data": [65.82, 50.46, 23.08, 88.37, 91.63, 92.6, 32.07, 96.43, 42.84, 75.18, 56.9],
                "bar_labels": ["Medieval Europe", "Prehistoric Era", "Industrial Revolution", "Military History",
                            "Archaeological Sites", "Renaissance", "Religious Movements", "Colonial History",
                            "Modern History", "Exploration History", "Ancient Civilizations"],
                "bar_colors": ["#73ECE2", "#AA6E28", "#EEA658", "#DE7676", "#FF69B4", "#ADCDF6", "#92D610",
                            "#FF7F50", "#BF7023", "#3DB60D", "#C02222"],
                "y_label": "Research Significance Score",
                "x_label": "Historical Topics",
                "img_title": "History & Archaeology Insights #10"
            }
        ],
        "22 - Weather & Climate": [
            {
                "bar_data": [78.5, 65.2, 89.3, 55.1, 92.4, 70.6, 83.7, 60.8, 74.9, 68.3],
                "bar_labels": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"],
                "bar_colors": ["#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF", "#33FFF5", "#F5FF33", "#FF8C33", "#8C33FF", "#33FF8C"],
                "y_label": "Average Annual Rainfall (inches)",
                "x_label": "City",
                "img_title": "Average Annual Rainfall by City"
            },
            {
                "bar_data": [30.2, 28.5, 35.1, 33.4, 29.8, 31.6, 27.9, 34.2, 32.5, 30.7],
                "bar_labels": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October"],
                "bar_colors": ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD", "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"],
                "y_label": "Average Monthly Temperature (°C)",
                "x_label": "Month",
                "img_title": "Average Monthly Temperatures"
            },
            {
                "bar_data": [120, 150, 180, 200, 170, 160, 190, 210, 220, 230],
                "bar_labels": ["Region A", "Region B", "Region C", "Region D", "Region E", "Region F", "Region G", "Region H", "Region I", "Region J"],
                "bar_colors": ["#FFB6C1", "#20B2AA", "#87CEFA", "#778899", "#B0C4DE", "#FFFFE0", "#00FA9A", "#48D1CC", "#C71585", "#191970"],
                "y_label": "Annual Sunshine Hours",
                "x_label": "Region",
                "img_title": "Annual Sunshine Hours by Region"
            },
            {
                "bar_data": [5.2, 6.1, 4.8, 5.5, 6.3, 5.9, 4.7, 5.8, 6.0, 5.6],
                "bar_labels": ["City A", "City B", "City C", "City D", "City E", "City F", "City G", "City H", "City I", "City J"],
                "bar_colors": ["#FF4500", "#2E8B57", "#1E90FF", "#DA70D6", "#32CD32", "#FFD700", "#00CED1", "#FF69B4", "#8A2BE2", "#5F9EA0"],
                "y_label": "Average Wind Speed (m/s)",
                "x_label": "City",
                "img_title": "Average Wind Speeds by City"
            },
            {
                "bar_data": [12, 15, 10, 14, 13, 11, 16, 9, 17, 8],
                "bar_labels": ["Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Zone 6", "Zone 7", "Zone 8", "Zone 9", "Zone 10"],
                "bar_colors": ["#DC143C", "#00FFFF", "#7FFF00", "#D2691E", "#FF7F50", "#6495ED", "#FFF8DC", "#8B0000", "#E9967A", "#8FBC8F"],
                "y_label": "Number of Storm Days per Year",
                "x_label": "Zone",
                "img_title": "Annual Storm Days by Zone"
            },
            {
                "bar_data": [25.4, 27.8, 22.1, 24.5, 26.3, 23.9, 28.0, 21.7, 29.2, 20.5],
                "bar_labels": ["Region X", "Region Y", "Region Z", "Region AA", "Region BB", "Region CC", "Region DD", "Region EE", "Region FF", "Region GG"],
                "bar_colors": ["#FF6347", "#40E0D0", "#EE82EE", "#F5DEB3", "#9ACD32", "#FF1493", "#00BFFF", "#696969", "#1E90FF", "#B22222"],
                "y_label": "Average Humidity (%)",
                "x_label": "Region",
                "img_title": "Average Humidity by Region"
            },
            {
                "bar_data": [300, 320, 310, 330, 340, 315, 325, 335, 345, 355],
                "bar_labels": ["Area 1", "Area 2", "Area 3", "Area 4", "Area 5", "Area 6", "Area 7", "Area 8", "Area 9", "Area 10"],
                "bar_colors": ["#FF00FF", "#00FFFF", "#FFFF00", "#800000", "#808000", "#008000", "#800080", "#008080", "#000080", "#FFA500"],
                "y_label": "Annual Snowfall (mm)",
                "x_label": "Area",
                "img_title": "Annual Snowfall by Area"
            },
            {
                "bar_data": [15.2, 16.5, 14.8, 17.1, 13.9, 18.3, 12.7, 19.4, 11.6, 20.5],
                "bar_labels": ["Location A", "Location B", "Location C", "Location D", "Location E", "Location F", "Location G", "Location H", "Location I", "Location J"],
                "bar_colors": ["#B0E0E6", "#FF69B4", "#CD5C5C", "#4B0082", "#F0E68C", "#E6E6FA", "#7CFC00", "#FFF0F5", "#ADD8E6", "#90EE90"],
                "y_label": "Average UV Index",
                "x_label": "Location",
                "img_title": "Average UV Index by Location"
            },
            {
                "bar_data": [60, 65, 70, 75, 80, 85, 90, 95, 100, 105],
                "bar_labels": ["Sector A", "Sector B", "Sector C", "Sector D", "Sector E", "Sector F", "Sector G", "Sector H", "Sector I", "Sector J"],
                "bar_colors": ["#FF4500", "#2E8B57", "#1E90FF", "#DA70D6", "#32CD32", "#FFD700", "#00CED1", "#FF69B4", "#8A2BE2", "#5F9EA0"],
                "y_label": "Air Quality Index (AQI)",
                "x_label": "Sector",
                "img_title": "Air Quality Index by Sector"
            },
            {
                "bar_data": [10.5, 12.3, 9.8, 11.7, 13.2, 8.9, 14.1, 7.6, 15.0, 6.4],
                "bar_labels": ["District 1", "District 2", "District 3", "District 4", "District 5", "District 6", "District 7", "District 8", "District 9", "District 10"],
                "bar_colors": ["#8B0000", "#FF8C00", "#2E8B57", "#1E90FF", "#DA70D6", "#32CD32", "#FFD700", "#00CED1", "#FF69B4", "#8A2BE2"],
                "y_label": "Average Cloud Cover (%)",
                "x_label": "District",
                "img_title": "Average Cloud Cover by District"
            }
        ],
        "23 - Transportation & Infrastructure": [
            {
                "bar_data": [320, 450, 290, 510, 430, 610, 370, 480, 520, 395],
                "bar_labels": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
                            "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"],
                "bar_colors": ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
                            "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"],
                "y_label": "Annual Commuter Rail Passengers (Millions)",
                "x_label": "City",
                "img_title": "Annual Rail Transit Ridership by City"
            },
            {
                "bar_data": [45.6, 52.8, 38.2, 49.0, 60.3, 41.7, 55.5, 47.8, 51.2, 43.9],
                "bar_labels": ["Line A", "Line B", "Line C", "Line D", "Line E",
                            "Line F", "Line G", "Line H", "Line I", "Line J"],
                "bar_colors": ["#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF",
                            "#33FFF5", "#F5FF33", "#FF8C33", "#8C33FF", "#33FF8C"],
                "y_label": "Track Length (km)",
                "x_label": "Transit Line",
                "img_title": "Subway Track Lengths by Line"
            },
            {
                "bar_data": [82, 94, 76, 101, 87, 96, 89, 92, 84, 79],
                "bar_labels": ["Terminal 1", "Terminal 2", "Terminal 3", "Terminal 4", "Terminal 5",
                            "Terminal 6", "Terminal 7", "Terminal 8", "Terminal 9", "Terminal 10"],
                "bar_colors": ["#8A2BE2", "#A52A2A", "#5F9EA0", "#7FFF00", "#D2691E",
                            "#FF7F50", "#6495ED", "#DC143C", "#00FFFF", "#00008B"],
                "y_label": "Passenger Handling Capacity (Millions)",
                "x_label": "Airport Terminal",
                "img_title": "Passenger Capacity by Airport Terminal"
            },
            {
                "bar_data": [125, 140, 110, 132, 118, 150, 107, 143, 130, 135],
                "bar_labels": ["Highway A", "Highway B", "Highway C", "Highway D", "Highway E",
                            "Highway F", "Highway G", "Highway H", "Highway I", "Highway J"],
                "bar_colors": ["#FF4500", "#2E8B57", "#1E90FF", "#DA70D6", "#32CD32",
                            "#FFD700", "#00CED1", "#FF69B4", "#8A2BE2", "#5F9EA0"],
                "y_label": "Traffic Volume (Thousands of Vehicles/Day)",
                "x_label": "Highway",
                "img_title": "Daily Traffic Volume by Highway"
            },
            {
                "bar_data": [35.5, 42.1, 39.6, 46.3, 33.9, 50.2, 37.4, 41.5, 44.7, 38.8],
                "bar_labels": ["Bridge A", "Bridge B", "Bridge C", "Bridge D", "Bridge E",
                            "Bridge F", "Bridge G", "Bridge H", "Bridge I", "Bridge J"],
                "bar_colors": ["#DC143C", "#00FFFF", "#7FFF00", "#D2691E", "#FF7F50",
                            "#6495ED", "#FFF8DC", "#8B0000", "#E9967A", "#8FBC8F"],
                "y_label": "Average Daily Crossings (Thousands)",
                "x_label": "Bridge",
                "img_title": "Daily Bridge Crossings"
            },
            {
                "bar_data": [12.3, 14.8, 11.1, 13.4, 10.9, 15.6, 9.8, 14.2, 13.9, 12.7],
                "bar_labels": ["Runway 1", "Runway 2", "Runway 3", "Runway 4", "Runway 5",
                            "Runway 6", "Runway 7", "Runway 8", "Runway 9", "Runway 10"],
                "bar_colors": ["#FF6347", "#40E0D0", "#EE82EE", "#F5DEB3", "#9ACD32",
                            "#FF1493", "#00BFFF", "#696969", "#1E90FF", "#B22222"],
                "y_label": "Runway Length (Thousands of Feet)",
                "x_label": "Airport Runway",
                "img_title": "Airport Runway Lengths"
            },
            {
                "bar_data": [95, 110, 88, 104, 90, 113, 87, 102, 108, 99],
                "bar_labels": ["Station A", "Station B", "Station C", "Station D", "Station E",
                            "Station F", "Station G", "Station H", "Station I", "Station J"],
                "bar_colors": ["#FF00FF", "#00FFFF", "#FFFF00", "#800000", "#808000",
                            "#008000", "#800080", "#008080", "#000080", "#FFA500"],
                "y_label": "Platform Length (Meters)",
                "x_label": "Train Station",
                "img_title": "Platform Lengths by Train Station"
            },
            {
                "bar_data": [25.1, 27.6, 24.3, 29.8, 26.7, 30.5, 23.4, 28.9, 27.1, 25.9],
                "bar_labels": ["Lot A", "Lot B", "Lot C", "Lot D", "Lot E",
                            "Lot F", "Lot G", "Lot H", "Lot I", "Lot J"],
                "bar_colors": ["#FFB6C1", "#20B2AA", "#87CEFA", "#778899", "#B0C4DE",
                            "#FFFFE0", "#00FA9A", "#48D1CC", "#C71585", "#191970"],
                "y_label": "Capacity (Hundreds of Vehicles)",
                "x_label": "Parking Lot",
                "img_title": "Parking Lot Capacity Comparison"
            },
            {
                "bar_data": [18.3, 22.5, 20.4, 24.9, 21.1, 23.7, 19.8, 25.2, 22.0, 20.7],
                "bar_labels": ["Tunnel A", "Tunnel B", "Tunnel C", "Tunnel D", "Tunnel E",
                            "Tunnel F", "Tunnel G", "Tunnel H", "Tunnel I", "Tunnel J"],
                "bar_colors": ["#FF4500", "#2E8B57", "#1E90FF", "#DA70D6", "#32CD32",
                            "#FFD700", "#00CED1", "#FF69B4", "#8A2BE2", "#5F9EA0"],
                "y_label": "Tunnel Length (km)",
                "x_label": "Tunnel",
                "img_title": "Tunnel Lengths in Major Metro Areas"
            }
        ],
        "24 - Psychology & Personality": [
            {
                "bar_data": [65.2, 72.3, 58.4, 80.1, 66.8, 74.5, 69.7, 77.2, 63.9, 70.6],
                "bar_labels": ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism",
                            "Honesty-Humility", "Patience", "Optimism", "Self-Efficacy", "Curiosity"],
                "bar_colors": ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
                            "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"],
                "y_label": "Average Trait Score",
                "x_label": "Personality Traits",
                "img_title": "Big Five & Related Personality Trait Scores"
            },
            {
                "bar_data": [42.3, 51.0, 39.7, 47.5, 56.2, 44.8, 50.3, 48.9, 53.1, 45.6],
                "bar_labels": ["Anxiety", "Depression", "Stress", "Self-esteem", "Motivation",
                            "Confidence", "Grit", "Resilience", "Mindfulness", "Emotional Stability"],
                "bar_colors": ["#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF",
                            "#33FFF5", "#F5FF33", "#FF8C33", "#8C33FF", "#33FF8C"],
                "y_label": "Psychological Scale Scores",
                "x_label": "Metrics",
                "img_title": "Psychological Assessment Scores"
            },
            {
                "bar_data": [23.1, 19.8, 25.6, 22.4, 20.9, 27.3, 24.5, 21.2, 26.7, 23.9],
                "bar_labels": ["Introversion", "Sensation Seeking", "Empathy", "Altruism", "Ambition",
                            "Leadership", "Social Anxiety", "Irritability", "Assertiveness", "Adaptability"],
                "bar_colors": ["#8A2BE2", "#A52A2A", "#5F9EA0", "#7FFF00", "#D2691E",
                            "#FF7F50", "#6495ED", "#DC143C", "#00FFFF", "#00008B"],
                "y_label": "Survey Ratings (0–30)",
                "x_label": "Behavioral Traits",
                "img_title": "Behavioral Trait Scores from Personality Survey"
            },
            {
                "bar_data": [12.3, 14.5, 11.7, 13.2, 15.6, 12.8, 14.1, 13.7, 12.9, 11.4],
                "bar_labels": ["Cognitive Flexibility", "Impulse Control", "Attention Span", "Working Memory", "Processing Speed",
                            "Problem Solving", "Spatial Reasoning", "Verbal Fluency", "Pattern Recognition", "Inhibitory Control"],
                "bar_colors": ["#FF6347", "#40E0D0", "#EE82EE", "#F5DEB3", "#9ACD32",
                            "#FF1493", "#00BFFF", "#696969", "#1E90FF", "#B22222"],
                "y_label": "Cognitive Skill Scores",
                "x_label": "Cognitive Abilities",
                "img_title": "Cognitive Abilities Across Domains"
            },
            {
                "bar_data": [76.5, 81.3, 74.9, 79.0, 83.1, 77.8, 80.6, 82.5, 78.4, 75.7],
                "bar_labels": ["Logical", "Linguistic", "Musical", "Bodily-Kinesthetic", "Spatial",
                            "Interpersonal", "Intrapersonal", "Naturalistic", "Existential", "Emotional"],
                "bar_colors": ["#FF00FF", "#00FFFF", "#FFFF00", "#800000", "#808000",
                            "#008000", "#800080", "#008080", "#000080", "#FFA500"],
                "y_label": "Intelligence Type Score",
                "x_label": "Multiple Intelligences",
                "img_title": "Multiple Intelligences Assessment Scores"
            },
            {
                "bar_data": [59, 63, 55, 61, 67, 60, 65, 64, 66, 62],
                "bar_labels": ["MBTI - ISTJ", "MBTI - ENFP", "MBTI - ISFJ", "MBTI - INTP", "MBTI - ESFJ",
                            "MBTI - ENTJ", "MBTI - ISFP", "MBTI - INFJ", "MBTI - ESTP", "MBTI - ENTP"],
                "bar_colors": ["#FF4500", "#2E8B57", "#1E90FF", "#DA70D6", "#32CD32",
                            "#FFD700", "#00CED1", "#FF69B4", "#8A2BE2", "#5F9EA0"],
                "y_label": "Distribution Percentage",
                "x_label": "MBTI Personality Types",
                "img_title": "MBTI Type Distribution in Sample Population"
            },
            {
                "bar_data": [88.2, 91.5, 86.4, 93.1, 89.7, 92.3, 90.4, 87.9, 94.2, 89.1],
                "bar_labels": ["Listening", "Speaking", "Decision Making", "Teamwork", "Leadership",
                            "Conflict Resolution", "Negotiation", "Creativity", "Empathy", "Time Management"],
                "bar_colors": ["#FFB6C1", "#20B2AA", "#87CEFA", "#778899", "#B0C4DE",
                            "#FFFFE0", "#00FA9A", "#48D1CC", "#C71585", "#191970"],
                "y_label": "Soft Skill Proficiency (%)",
                "x_label": "Skills",
                "img_title": "Soft Skills Proficiency Assessment"
            },
            {
                "bar_data": [7.5, 8.9, 6.3, 9.1, 8.7, 9.3, 7.9, 8.4, 6.8, 7.2],
                "bar_labels": ["Introversion", "Extroversion", "Agreeableness", "Openness", "Resilience",
                            "Perfectionism", "Compulsiveness", "Risk Aversion", "Neuroticism", "Altruism"],
                "bar_colors": ["#DC143C", "#00FFFF", "#7FFF00", "#D2691E", "#FF7F50",
                            "#6495ED", "#FFF8DC", "#8B0000", "#E9967A", "#8FBC8F"],
                "y_label": "Z-Score",
                "x_label": "Personality Trait (Normalized)",
                "img_title": "Z-Scores for Selected Personality Traits"
            },
            {
                "bar_data": [68.9, 71.2, 65.5, 72.8, 69.7, 73.5, 70.3, 66.8, 74.1, 67.4],
                "bar_labels": ["Trust", "Kindness", "Fairness", "Gratitude", "Forgiveness",
                            "Modesty", "Prudence", "Hope", "Spirituality", "Humility"],
                "bar_colors": ["#B0E0E6", "#FF69B4", "#CD5C5C", "#4B0082", "#F0E68C",
                            "#E6E6FA", "#7CFC00", "#FFF0F5", "#ADD8E6", "#90EE90"],
                "y_label": "Moral Value Strength",
                "x_label": "Character Traits",
                "img_title": "Strength of Character Traits"
            },
            {
                "bar_data": [32.4, 36.8, 29.7, 38.2, 34.9, 40.1, 35.7, 37.5, 33.3, 31.8],
                "bar_labels": ["Paranoia", "Narcissism", "Machiavellianism", "Psychopathy", "Impulsivity",
                            "Manipulativeness", "Jealousy", "Egocentrism", "Suspicion", "Aggressiveness"],
                "bar_colors": ["#800000", "#808000", "#008000", "#800080", "#008080",
                            "#000080", "#FFA07A", "#20B2AA", "#778899", "#CD5C5C"],
                "y_label": "Dark Trait Index",
                "x_label": "Traits",
                "img_title": "Assessment of Dark Personality Traits"
            }
        ],
        "25 - Materials & Engineering": [
            {
                "bar_data": [7850, 2700, 4500, 8900, 2320, 19300, 3500, 890, 1190, 2710],
                "bar_labels": ["Steel", "Aluminum", "Titanium", "Copper", "Carbon Fiber",
                            "Tungsten", "Brass", "Balsa Wood", "ABS Plastic", "Magnesium"],
                "bar_colors": ["#A52A2A", "#FFA500", "#4682B4", "#B22222", "#2E8B57",
                            "#4B0082", "#FFD700", "#D2691E", "#8A2BE2", "#00CED1"],
                "y_label": "Density (kg/m³)",
                "x_label": "Material",
                "img_title": "Density of Common Engineering Materials"
            },
            {
                "bar_data": [200, 70, 116, 110, 500, 400, 100, 80, 130, 150],
                "bar_labels": ["Steel", "Aluminum", "Brass", "Bronze", "Carbon Fiber",
                            "Titanium", "Plastic", "Wood", "Glass", "Magnesium"],
                "bar_colors": ["#FF7F50", "#1E90FF", "#FFD700", "#DA70D6", "#2E8B57",
                            "#A52A2A", "#8B008B", "#FF6347", "#4682B4", "#B0C4DE"],
                "y_label": "Tensile Strength (MPa)",
                "x_label": "Material",
                "img_title": "Tensile Strength of Various Materials"
            },
            {
                "bar_data": [80, 205, 110, 180, 75, 90, 140, 125, 160, 130],
                "bar_labels": ["Concrete", "Steel", "Glass", "Aluminum", "Wood",
                            "Polycarbonate", "Brass", "Carbon Fiber", "Ceramic", "Titanium"],
                "bar_colors": ["#B8860B", "#2F4F4F", "#D2B48C", "#FF4500", "#ADFF2F",
                            "#20B2AA", "#FF8C00", "#00FA9A", "#9932CC", "#708090"],
                "y_label": "Elastic Modulus (GPa)",
                "x_label": "Material",
                "img_title": "Elastic Modulus Comparison of Engineering Materials"
            },
            {
                "bar_data": [16, 237, 429, 54, 401, 0.2, 385, 50, 110, 210],
                "bar_labels": ["Stainless Steel", "Aluminum", "Silver", "Titanium", "Copper",
                            "Wood", "Gold", "Glass", "Brass", "Graphene"],
                "bar_colors": ["#C0C0C0", "#B0E0E6", "#FFD700", "#DAA520", "#CD5C5C",
                            "#8B4513", "#FF69B4", "#D8BFD8", "#6495ED", "#2F4F4F"],
                "y_label": "Thermal Conductivity (W/m·K)",
                "x_label": "Material",
                "img_title": "Thermal Conductivity of Materials"
            },
            {
                "bar_data": [55, 34, 70, 40, 85, 95, 60, 30, 90, 65],
                "bar_labels": ["Recycled Steel", "Bamboo", "Cross-Laminated Timber", "Rammed Earth", "Aerogel",
                            "Carbon Fiber", "Cork", "Sheep Wool", "Straw Bales", "Hempcrete"],
                "bar_colors": ["#8FBC8F", "#DAA520", "#C71585", "#8B0000", "#20B2AA",
                            "#2E8B57", "#FF6347", "#00CED1", "#D2691E", "#9370DB"],
                "y_label": "Sustainability Index",
                "x_label": "Material",
                "img_title": "Sustainability Scores of Eco-friendly Materials"
            },
            {
                "bar_data": [6, 8.2, 10, 7.5, 12, 11.3, 5.6, 9, 10.5, 8],
                "bar_labels": ["Concrete", "Steel", "Aluminum", "Brick", "Glass",
                            "Fiber Cement", "Wood", "Bamboo", "Ceramics", "Plastic"],
                "bar_colors": ["#696969", "#708090", "#4682B4", "#A52A2A", "#ADD8E6",
                            "#556B2F", "#CD853F", "#DAA520", "#8B008B", "#D2B48C"],
                "y_label": "Cost per Unit Volume ($/ft³)",
                "x_label": "Material",
                "img_title": "Cost Comparison of Building Materials"
            },
            {
                "bar_data": [5000, 7000, 11000, 3500, 6000, 9000, 12000, 10000, 8000, 7500],
                "bar_labels": ["High Strength Steel", "Aluminum Alloy", "Titanium Alloy", "Copper Alloy", "Cast Iron",
                            "Magnesium Alloy", "Carbon Fiber", "Kevlar", "Glass Fiber", "Bronze"],
                "bar_colors": ["#DC143C", "#FF8C00", "#483D8B", "#FFD700", "#B22222",
                            "#8FBC8F", "#5F9EA0", "#8B0000", "#B0C4DE", "#DAA520"],
                "y_label": "Yield Strength (psi)",
                "x_label": "Material",
                "img_title": "Yield Strength of High-Performance Materials"
            },
            {
                "bar_data": [0.12, 0.34, 0.25, 0.30, 0.22, 0.18, 0.27, 0.31, 0.29, 0.24],
                "bar_labels": ["Steel", "Aluminum", "Copper", "Titanium", "Plastic",
                            "Glass", "Carbon Fiber", "Concrete", "Wood", "Rubber"],
                "bar_colors": ["#4682B4", "#B0E0E6", "#CD5C5C", "#FFD700", "#9370DB",
                            "#708090", "#2E8B57", "#D2691E", "#A0522D", "#8B008B"],
                "y_label": "Poisson's Ratio",
                "x_label": "Material",
                "img_title": "Poisson's Ratio Across Materials"
            },
            {
                "bar_data": [98, 89, 93, 87, 95, 92, 88, 91, 94, 86],
                "bar_labels": ["Epoxy Resin", "Acrylic", "Polyester", "Nylon", "Polyurethane",
                            "Silicone", "Polycarbonate", "PVC", "Teflon", "ABS"],
                "bar_colors": ["#FF1493", "#00BFFF", "#8B0000", "#ADFF2F", "#4B0082",
                            "#FFA07A", "#20B2AA", "#778899", "#800000", "#FFD700"],
                "y_label": "Adhesion Strength (MPa)",
                "x_label": "Polymeric Material",
                "img_title": "Adhesion Strength of Polymer Materials"
            },
            {
                "bar_data": [12, 10, 8, 9, 11, 13, 7, 6, 14, 15],
                "bar_labels": ["Steel Beam", "Concrete Slab", "Wood Joist", "Aluminum Truss", "PVC Pipe",
                            "Carbon Tube", "Glass Sheet", "Rubber Support", "Titanium Bar", "Plastic Panel"],
                "bar_colors": ["#DC143C", "#8B4513", "#DEB887", "#6495ED", "#2E8B57",
                            "#4B0082", "#20B2AA", "#CD5C5C", "#FFD700", "#ADFF2F"],
                "y_label": "Load Bearing Capacity (tons)",
                "x_label": "Structural Element",
                "img_title": "Load Capacity of Structural Elements"
            }
        ],
        "26 - Philanthropy & Charity": [
            {
                "bar_data": [890, 760, 520, 670, 430, 390, 610, 580, 455, 490],
                "bar_labels": ["Red Cross", "UNICEF", "WWF", "Doctors Without Borders", "Save the Children",
                            "CARE", "Charity: Water", "Feeding America", "Direct Relief", "Oxfam"],
                "bar_colors": ["#E74C3C", "#2980B9", "#27AE60", "#F1C40F", "#9B59B6",
                            "#E67E22", "#1ABC9C", "#34495E", "#A93226", "#7D3C98"],
                "y_label": "Annual Donations Received ($ Millions)",
                "x_label": "Organizations",
                "img_title": "Top Global Charities by Annual Donations"
            },
            {
                "bar_data": [25, 33, 40, 28, 22, 18, 30, 35, 26, 19],
                "bar_labels": ["Bill & Melinda Gates Foundation", "Wellcome Trust", "Howard Buffett Foundation",
                            "Ford Foundation", "Bloomberg Philanthropies", "Walton Family Foundation", 
                            "Open Society Foundations", "Packard Foundation", "Rockefeller Foundation", "Skoll Foundation"],
                "bar_colors": ["#3498DB", "#1ABC9C", "#E74C3C", "#F39C12", "#8E44AD",
                            "#E67E22", "#2ECC71", "#9B59B6", "#16A085", "#C0392B"],
                "y_label": "Annual Grant Spending ($ Billion)",
                "x_label": "Philanthropic Foundations",
                "img_title": "Major Philanthropic Foundations by Grant Spending"
            },
            {
                "bar_data": [72, 55, 48, 60, 38, 33, 45, 52, 40, 29],
                "bar_labels": ["USA", "UK", "Germany", "Canada", "Australia",
                            "France", "Sweden", "Japan", "Netherlands", "India"],
                "bar_colors": ["#2980B9", "#E67E22", "#16A085", "#8E44AD", "#C0392B",
                            "#F1C40F", "#2ECC71", "#D35400", "#3498DB", "#A93226"],
                "y_label": "Total International Aid ($ Billion)",
                "x_label": "Countries",
                "img_title": "Top Countries in International Aid Contributions"
            },
            {
                "bar_data": [60, 42, 38, 50, 33, 25, 47, 52, 39, 30],
                "bar_labels": ["Disaster Relief", "Education", "Healthcare", "Poverty Alleviation", "Refugee Support",
                            "Animal Welfare", "Environmental Protection", "Clean Water", "Women Empowerment", "Child Welfare"],
                "bar_colors": ["#E74C3C", "#2E86C1", "#27AE60", "#F39C12", "#8E44AD",
                            "#3498DB", "#1ABC9C", "#F4D03F", "#A569BD", "#CA6F1E"],
                "y_label": "Donor Interest Level (Index)",
                "x_label": "Cause Area",
                "img_title": "Popular Causes Among Global Donors"
            },
            {
                "bar_data": [12, 17, 9, 14, 10, 6, 11, 15, 13, 8],
                "bar_labels": ["Facebook", "GoFundMe", "Patreon", "JustGiving", "GlobalGiving",
                            "Kickstarter", "Classy", "Fundly", "CrowdRise", "Indiegogo"],
                "bar_colors": ["#3B5998", "#00BFA5", "#FF5700", "#FF6F61", "#1ABC9C",
                            "#4CAF50", "#E67E22", "#6C3483", "#CA6F1E", "#3498DB"],
                "y_label": "Online Donations Facilitated ($ Billion)",
                "x_label": "Fundraising Platform",
                "img_title": "Top Online Crowdfunding Platforms by Donations"
            },
            {
                "bar_data": [85, 78, 66, 73, 69, 64, 71, 75, 68, 62],
                "bar_labels": ["Health", "Food Aid", "Shelter", "Education", "Sanitation",
                            "Child Protection", "Mental Health", "Legal Aid", "Clean Water", "Energy"],
                "bar_colors": ["#F1948A", "#D5F5E3", "#F5CBA7", "#BB8FCE", "#73C6B6",
                            "#E59866", "#85C1E9", "#F7DC6F", "#DC7633", "#82E0AA"],
                "y_label": "Funding Priority Score (1–100)",
                "x_label": "Humanitarian Need",
                "img_title": "Humanitarian Funding Priority by Sector"
            },
            {
                "bar_data": [1500, 1200, 900, 1300, 1100, 1000, 950, 980, 870, 760],
                "bar_labels": ["Corporate Donations", "Foundations", "Individual Donors", "Bequests", "Government Grants",
                            "Religious Groups", "NGOs", "CSR Programs", "Events", "Crowdfunding"],
                "bar_colors": ["#C0392B", "#8E44AD", "#2980B9", "#F39C12", "#2ECC71",
                            "#D35400", "#1ABC9C", "#7D3C98", "#A93226", "#3498DB"],
                "y_label": "Donation Volume ($ Millions)",
                "x_label": "Source",
                "img_title": "Breakdown of Global Charity Funding Sources"
            },
            {
                "bar_data": [4.2, 3.8, 2.5, 3.6, 3.1, 2.2, 3.9, 3.3, 2.8, 2.7],
                "bar_labels": ["Hurricane Katrina", "COVID-19 Relief", "Tsunami 2004", "Ebola Crisis", "Ukraine Conflict",
                            "Haiti Earthquake", "Pakistan Floods", "Syria Refugee Crisis", "Nepal Earthquake", "Turkey-Syria Quake"],
                "bar_colors": ["#E74C3C", "#1ABC9C", "#F39C12", "#8E44AD", "#3498DB",
                            "#D35400", "#9B59B6", "#2ECC71", "#34495E", "#C0392B"],
                "y_label": "Funds Raised ($ Billion)",
                "x_label": "Disaster Event",
                "img_title": "Funds Raised for Major Humanitarian Disasters"
            },
            {
                "bar_data": [87, 73, 65, 79, 68, 54, 76, 70, 63, 58],
                "bar_labels": ["Transparency", "Efficiency", "Impact Reporting", "Governance", "Donor Trust",
                            "Sustainability", "Accessibility", "Local Involvement", "Tech Use", "Innovation"],
                "bar_colors": ["#58D68D", "#5DADE2", "#F5B041", "#AF7AC5", "#EC7063",
                            "#48C9B0", "#F4D03F", "#C39BD3", "#5499C7", "#F7DC6F"],
                "y_label": "Charity Evaluation Index",
                "x_label": "Assessment Criteria",
                "img_title": "Top Factors in Charity Evaluation"
            },
            {
                "bar_data": [450, 390, 520, 470, 410, 360, 430, 490, 445, 380],
                "bar_labels": ["Healthcare NGOs", "Education NGOs", "Disaster Relief NGOs", "Environment NGOs", "Food Banks",
                            "Child Protection NGOs", "Human Rights NGOs", "Community NGOs", "Animal Shelters", "Homeless Aid"],
                "bar_colors": ["#DC7633", "#2980B9", "#58D68D", "#C0392B", "#F1C40F",
                            "#8E44AD", "#3498DB", "#E67E22", "#2ECC71", "#F39C12"],
                "y_label": "Active Projects Worldwide",
                "x_label": "NGO Type",
                "img_title": "Global NGO Activity by Sector"
            }
        ],
        "27 - Fashion & Apparel": [
            {
                "bar_data": [82.1, 74.5, 69.3, 61.7, 59.8, 54.4, 47.6, 42.9, 39.2, 36.5],
                "bar_labels": ["Nike", "Adidas", "Zara", "H&M", "Louis Vuitton", "Uniqlo", "Chanel", "Hermès", "Gucci", "Rolex"],
                "bar_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#9B59B6", "#F1C40F",
                            "#1ABC9C", "#E67E22", "#8E44AD", "#34495E", "#D35400"],
                "y_label": "Brand Value ($ Billion)",
                "x_label": "Brands",
                "img_title": "Top Fashion Brands by Global Brand Value"
            },
            {
                "bar_data": [23.7, 19.4, 17.9, 15.2, 14.5, 13.6, 12.1, 11.5, 10.3, 9.7],
                "bar_labels": ["LVMH", "Inditex", "Nike Inc.", "Adidas AG", "Kering", "H&M Group",
                            "Richemont", "PVH Corp", "Under Armour", "Fast Retailing"],
                "bar_colors": ["#1F618D", "#F39C12", "#27AE60", "#8E44AD", "#D35400",
                            "#3498DB", "#C0392B", "#F5B041", "#16A085", "#7D3C98"],
                "y_label": "Annual Revenue ($ Billion)",
                "x_label": "Fashion Corporations",
                "img_title": "Leading Fashion Companies by Annual Revenue"
            },
            {
                "bar_data": [55, 48, 43, 39, 36, 32, 29, 28, 26, 23],
                "bar_labels": ["USA", "China", "India", "Italy", "France", "Vietnam", "Germany", "Turkey", "Bangladesh", "UK"],
                "bar_colors": ["#3498DB", "#E67E22", "#27AE60", "#9B59B6", "#C0392B",
                            "#F1C40F", "#1ABC9C", "#8E44AD", "#2ECC71", "#E74C3C"],
                "y_label": "Clothing Exports ($ Billion)",
                "x_label": "Countries",
                "img_title": "Top Clothing Exporting Countries"
            },
            {
                "bar_data": [10.5, 9.2, 8.7, 8.0, 7.4, 6.9, 6.2, 5.7, 5.2, 4.9],
                "bar_labels": ["Jeans", "T-shirts", "Sneakers", "Dresses", "Jackets", "Sweaters", "Shirts", "Shorts", "Suits", "Hoodies"],
                "bar_colors": ["#2ECC71", "#F39C12", "#2980B9", "#E74C3C", "#8E44AD",
                            "#1ABC9C", "#F5B041", "#C0392B", "#5DADE2", "#7D3C98"],
                "y_label": "Annual Sales Volume (Billions of Units)",
                "x_label": "Apparel Types",
                "img_title": "Top-Selling Apparel Items Globally"
            },
            {
                "bar_data": [49, 44, 41, 38, 35, 33, 30, 28, 26, 24],
                "bar_labels": ["Spring", "Summer", "Fall", "Winter", "Black Friday", "Holiday Season", "Back to School",
                            "Valentine's Day", "Mother's Day", "Cyber Monday"],
                "bar_colors": ["#F1948A", "#F5B041", "#BB8FCE", "#48C9B0", "#E67E22",
                            "#3498DB", "#C39BD3", "#F7DC6F", "#CA6F1E", "#85C1E9"],
                "y_label": "Fashion Sales Index",
                "x_label": "Seasons & Events",
                "img_title": "Peak Fashion Sales Periods by Season/Event"
            },
            {
                "bar_data": [35, 30, 28, 26, 24, 23, 21, 20, 18, 17],
                "bar_labels": ["Fast Fashion", "Luxury", "Athleisure", "Streetwear", "Vintage", "Eco-Friendly", "Minimalist",
                            "Techwear", "Boho", "Gothic"],
                "bar_colors": ["#1ABC9C", "#F39C12", "#8E44AD", "#C0392B", "#3498DB",
                            "#27AE60", "#E67E22", "#9B59B6", "#F7DC6F", "#34495E"],
                "y_label": "Popularity Score (0–100)",
                "x_label": "Fashion Styles",
                "img_title": "Most Popular Fashion Styles Globally"
            },
            {
                "bar_data": [72, 65, 59, 53, 48, 45, 41, 39, 36, 33],
                "bar_labels": ["Cotton", "Polyester", "Silk", "Wool", "Linen", "Nylon", "Rayon", "Denim", "Spandex", "Bamboo"],
                "bar_colors": ["#3498DB", "#E74C3C", "#9B59B6", "#2ECC71", "#F39C12",
                            "#8E44AD", "#1ABC9C", "#C0392B", "#F5B041", "#48C9B0"],
                "y_label": "Material Usage Index",
                "x_label": "Fabric Types",
                "img_title": "Most Common Materials Used in Fashion"
            },
            {
                "bar_data": [68, 61, 58, 55, 50, 47, 45, 42, 39, 35],
                "bar_labels": ["Sustainability", "Digital Fitting", "3D Printing", "Smart Fabrics", "Rental Fashion",
                            "Virtual Try-On", "Blockchain Tracking", "AR Runways", "Custom Tailoring", "Biodegradable Fabric"],
                "bar_colors": ["#1ABC9C", "#F1C40F", "#8E44AD", "#2ECC71", "#E74C3C",
                            "#3498DB", "#F39C12", "#BB8FCE", "#5DADE2", "#CA6F1E"],
                "y_label": "Innovation Adoption Score",
                "x_label": "Fashion Technologies",
                "img_title": "Emerging Technologies in Fashion Industry"
            },
            {
                "bar_data": [22.3, 20.1, 18.5, 17.6, 16.8, 15.2, 14.7, 13.9, 12.5, 11.4],
                "bar_labels": ["ASOS", "Shein", "Zalando", "Boohoo", "Nordstrom", "Myntra", "Revolve", "Farfetch", "Lulus", "PrettyLittleThing"],
                "bar_colors": ["#E67E22", "#C0392B", "#2ECC71", "#3498DB", "#F39C12",
                            "#8E44AD", "#1ABC9C", "#F7DC6F", "#9B59B6", "#CA6F1E"],
                "y_label": "Annual Online Sales ($ Billion)",
                "x_label": "E-Commerce Fashion Retailers",
                "img_title": "Top Online Fashion Retailers by Sales"
            },
            {
                "bar_data": [30, 27, 24, 22, 20, 18, 17, 15, 14, 12],
                "bar_labels": ["Jeans", "Sneakers", "Watches", "Hoodies", "Caps", "Sunglasses", "Belts", "Dresses", "Boots", "Scarves"],
                "bar_colors": ["#2ECC71", "#E74C3C", "#9B59B6", "#3498DB", "#F39C12",
                            "#1ABC9C", "#8E44AD", "#F5B041", "#CA6F1E", "#7D3C98"],
                "y_label": "Accessory Sales Volume (Millions)",
                "x_label": "Items",
                "img_title": "Top-Selling Fashion Accessories"
            }
        ],
        "28 - Parenting & Child Development": [
            {
                "bar_data": [54.63, 36.97, 50.37, 54.80, 25.90, 15.50, 21.40, 31.36, 50.90, 53.04],
                "bar_labels": ["0-1 yrs", "1-2 yrs", "2-3 yrs", "3-4 yrs", "4-5 yrs", "5-6 yrs", "6-7 yrs", "7-8 yrs", "8-9 yrs", "9-10 yrs"],
                "bar_colors": ["#33A1FF", "#FF5733", "#33FF57", "#FF33E1", "#8DFF33", "#D7FF33", "#A1FF33", "#3357FF", "#FFC733", "#A833FF"],
                "y_label": "Hours",
                "x_label": "Age Group",
                "img_title": "Average Daily Screen Time by Age Group"
            },
            {
                "bar_data": [10.35, 35.54, 30.87, 21.11, 15.99, 26.88, 57.15, 26.16, 35.94, 45.15],
                "bar_labels": ["Authoritative", "Authoritarian", "Permissive", "Uninvolved", "Attachment-Based", "Helicopter", "Free-range", "Positive", "Tiger", "Gentle"],
                "bar_colors": ["#D7FF33", "#FF33E1", "#C133FF", "#A1FF33", "#8DFF33", "#33A1FF", "#FF3333", "#F233FF", "#33FF8D", "#33C1FF"],
                "y_label": "GPA Score",
                "x_label": "Parenting Style",
                "img_title": "Impact of Parenting Styles on Academic Performance"
            },
            {
                "bar_data": [28.18, 58.59, 58.12, 22.59, 34.86, 25.04, 24.24, 11.84, 40.48, 35.13],
                "bar_labels": ["1 yr", "2 yrs", "3 yrs", "4 yrs", "5 yrs", "6 yrs", "7 yrs", "8 yrs", "9 yrs", "10 yrs"],
                "bar_colors": ["#FF5733", "#A1FF33", "#8DFF33", "#FFC733", "#F233FF", "#FF3333", "#33FFF2", "#FF33E1", "#C133FF", "#FF9A33"],
                "y_label": "Issue Frequency (%)",
                "x_label": "Age Group",
                "img_title": "Common Behavioral Issues by Age"
            },
            {
                "bar_data": [12.57, 23.93, 55.41, 21.98, 17.24, 34.47, 59.28, 22.10, 43.61, 48.08],
                "bar_labels": ["Montessori", "Waldorf", "Reggio Emilia", "Play-based", "Academic", "Structured", "Unschooling", "Home-based", "Outdoor", "Tech-assisted"],
                "bar_colors": ["#C133FF", "#D7FF33", "#FFC733", "#FF9A33", "#FF33A8", "#A1FF33", "#33A1FF", "#8DFF33", "#33FF8D", "#A833FF"],
                "y_label": "Effectiveness Score",
                "x_label": "Learning Method",
                "img_title": "Effectiveness of Early Learning Methods"
            },
            {
                "bar_data": [21.88, 46.41, 28.39, 41.62, 41.68, 36.79, 14.51, 51.77, 26.04, 19.33],
                "bar_labels": ["Iron", "Calcium", "Vitamin D", "Zinc", "Folate", "Vitamin A", "Vitamin C", "Magnesium", "Omega-3", "Fiber"],
                "bar_colors": ["#FF9A33", "#33FFD7", "#8DFF33", "#F233FF", "#33A1FF", "#C133FF", "#FF8C33", "#FF33A8", "#FF3333", "#A1FF33"],
                "y_label": "Avg Daily Intake (mg)",
                "x_label": "Nutrient",
                "img_title": "Nutrient Intake Comparison in Toddlers"
            },
            {
                "bar_data": [12.04, 39.54, 43.88, 10.83, 35.60, 21.32, 42.26, 18.72, 44.55, 29.34],
                "bar_labels": ["0-1 yrs", "1-2 yrs", "2-3 yrs", "3-4 yrs", "4-5 yrs", "5-6 yrs", "6-7 yrs", "7-8 yrs", "8-9 yrs", "9-10 yrs"],
                "bar_colors": ["#33FF8D", "#33A1FF", "#33C1FF", "#FF8C33", "#A1FF33", "#FF3333", "#33FF57", "#C133FF", "#FF33A8", "#F233FF"],
                "y_label": "Avg Sleep (Hours)",
                "x_label": "Age Group",
                "img_title": "Sleep Patterns by Age Group"
            },
            {
                "bar_data": [56.84, 16.88, 27.05, 15.67, 56.23, 53.87, 22.90, 43.00, 50.86, 37.76],
                "bar_labels": ["Feeding", "Sleep", "Crying", "Milestones", "Bonding", "Illness", "Teething", "Growth", "Mobility", "Safety"],
                "bar_colors": ["#FF33E1", "#33FF57", "#D7FF33", "#A833FF", "#FF8C33", "#FF3333", "#3357FF", "#33FFF2", "#C133FF", "#FF9A33"],
                "y_label": "Concern Level (1-10)",
                "x_label": "Concern",
                "img_title": "Top Concerns of New Parents"
            },
            {
                "bar_data": [36.48, 22.09, 14.66, 54.86, 55.02, 41.66, 26.95, 27.46, 46.30, 54.86],
                "bar_labels": ["Feeding", "Bathing", "Playing", "Teaching", "Outdoor Time", "Diapering", "Nap Supervision", "Reading", "Transporting", "Health Checkups"],
                "bar_colors": ["#D7FF33", "#A1FF33", "#C133FF", "#33FF8D", "#FF9A33", "#33FFD7", "#8DFF33", "#33FFF2", "#FFC733", "#F233FF"],
                "y_label": "Hours per Week",
                "x_label": "Activity",
                "img_title": "Time Spent on Childcare Activities (Weekly)"
            },
            {
                "bar_data": [54.35, 48.99, 42.10, 14.21, 18.08, 54.93, 40.32, 10.46, 15.07, 43.18],
                "bar_labels": ["Sweden", "Norway", "Canada", "Germany", "France", "Japan", "South Korea", "Australia", "UK", "USA"],
                "bar_colors": ["#FF9A33", "#8DFF33", "#FF33A8", "#33C1FF", "#A833FF", "#3357FF", "#FF33E1", "#A1FF33", "#33FF8D", "#33A1FF"],
                "y_label": "Weeks of Leave",
                "x_label": "Country",
                "img_title": "Parental Leave Policies by Country"
            },
            {
                "bar_data": [10.25, 18.04, 37.44, 44.59, 42.60, 21.21, 45.61, 21.86, 26.27, 47.32],
                "bar_labels": ["Milestone Tracking", "Sleep Monitoring", "Feeding Logs", "Health Alerts", "Community Forum", "Growth Charts", "Learning Games", "Appointment Scheduler", "Mood Tracking", "Daily Tips"],
                "bar_colors": ["#FF33A8", "#33FF57", "#33FFF2", "#8DFF33", "#33FF8D", "#FF5733", "#FF8C33", "#C133FF", "#FF9A33", "#33C1FF"],
                "y_label": "Usage Frequency (%)",
                "x_label": "Feature",
                "img_title": "Usage of Parenting Apps by Feature"
            }
        ],
        "29 - Architecture & Urban Planning": [
            {
                "bar_data": [56.5, 47.6, 37.4, 33.7, 33.1, 28.6, 27.6, 26.7, 26.4, 26.2],
                "bar_labels": ["New York City", "Jersey City", "Washington D.C.", "Boston", "San Francisco", "Cambridge", "Chicago", "Newark", "Arlington", "Philadelphia"],
                "bar_colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
                "y_label": "Public Transit Commuters (%)",
                "x_label": "City",
                "img_title": "Top U.S. Cities by Public Transit Commuter Percentage"
            },
            {
                "bar_data": [88.0, 77.2, 74.4, 67.3, 66.6, 60.7, 51.1, 49.2, 45.0, 41.4],
                "bar_labels": ["New York", "Chicago", "Seattle", "Portland", "Buffalo", "Rochester", "Detroit", "Spokane", "San Bernardino", "Phoenix"],
                "bar_colors": ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf", "#999999", "#66c2a5"],
                "y_label": "Walk Score",
                "x_label": "City",
                "img_title": "Walkability Scores of Major U.S. Cities"
            },
            {
                "bar_data": [12.2, 11.0, 10.4, 10.0, 10.0, 9.6, 8.5, 7.7, 7.7, 7.2],
                "bar_labels": ["Los Angeles", "San Jose", "Long Beach", "San Francisco", "New York", "San Diego", "Miami", "Boston", "Oakland", "Seattle"],
                "bar_colors": ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#666666", "#1f78b4", "#b2df8a"],
                "y_label": "Home Price-to-Income Ratio",
                "x_label": "City",
                "img_title": "Housing Affordability in Major U.S. Cities"
            },
            {
                "bar_data": [1023, 870, 856, 146, 166, 168, 200, 250, 300, 350],
                "bar_labels": ["Atlanta", "Dallas", "Portland", "New York", "Miami", "Boston", "Chicago", "Los Angeles", "San Francisco", "Seattle"],
                "bar_colors": ["#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a"],
                "y_label": "Green Space per Capita (sq ft)",
                "x_label": "City",
                "img_title": "Urban Green Space Availability in U.S. Cities"
            },
            {
                "bar_data": [91, 80, 71.4, 68.8, 67.7, 58.6, 58.5, 58.1, 57.2, 56.8],
                "bar_labels": ["Seattle", "National Average", "Dallas", "Austin", "Houston", "San Antonio", "Chicago", "Los Angeles", "San Diego", "Phoenix"],
                "bar_colors": ["#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd"],
                "y_label": "Annual Income Needed for Rent ($K)",
                "x_label": "City",
                "img_title": "Annual Income Required to Afford Rent in U.S. Cities"
            },
            {
                "bar_data": [233.3, 200.0, 180.0, 150.0, 140.0, 130.0, 120.0, 110.0, 100.0, 90.0],
                "bar_labels": ["Kuala Lumpur", "Dubai", "Shanghai", "New York", "Chicago", "Hong Kong", "Toronto", "London", "Sydney", "Tokyo"],
                "bar_colors": ["#ff8c00", "#e9967a", "#8fbc8f", "#483d8b", "#2e8b57", "#d2691e", "#5f9ea0", "#9acd32", "#ff1493", "#00ced1"],
                "y_label": "Average Building Height (m)",
                "x_label": "City",
                "img_title": "Average Building Heights in Global Cities"
            },
            {
                "bar_data": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55],
                "bar_labels": ["City A", "City B", "City C", "City D", "City E", "City F", "City G", "City H", "City I", "City J"],
                "bar_colors": ["#ff4500", "#da70d6", "#7fff00", "#d2691e", "#6495ed", "#ff69b4", "#cd5c5c", "#ffa500", "#40e0d0", "#9acd32"],
                "y_label": "Urban Density (People per Hectare)",
                "x_label": "City",
                "img_title": "Urban Density Comparison Across Cities"
            },
            {
                "bar_data": [75, 70, 65, 60, 55, 50, 45, 40, 35, 30],
                "bar_labels": ["City K", "City L", "City M", "City N", "City O", "City P", "City Q", "City R", "City S", "City T"],
                "bar_colors": ["#ff6347", "#4682b4", "#daa520", "#32cd32", "#ba55d3", "#3cb371", "#b0c4de", "#ff4500", "#2e8b57", "#ff1493"],
                "y_label": "Percentage of Land Used for Residential",
                "x_label": "City",
                "img_title": "Residential Land Use Percentage in Various Cities"
            },
            {
                "bar_data": [60, 55, 50, 45, 40, 35, 30, 25, 20, 15],
                "bar_labels": ["City U", "City V", "City W", "City X", "City Y", "City Z", "City AA", "City AB", "City AC", "City AD"],
                "bar_colors": ["#ff7f50", "#6a5acd", "#20b2aa", "#ff69b4", "#cd853f", "#b0e0e6", "#ff4500", "#2e8b57", "#ff1493", "#00ced1"],
                "y_label": "Public Transportation Coverage (%)",
                "x_label": "City",
                "img_title": "Public Transportation Coverage in Different Cities"
            },
            {
                "bar_data": [85, 80, 75, 70, 65, 60, 55, 50, 45, 40],
                "bar_labels": ["City AE", "City AF", "City AG", "City AH", "City AI", "City AJ", "City AK", "City AL", "City AM", "City AN"],
                "bar_colors": ["#7fffd4", "#ff69b4", "#cd5c5c", "#ffa500", "#40e0d0", "#9acd32", "#ff4500", "#da70d6", "#7fff00", "#d2691e"],
                "y_label": "Sustainable Building Practices Score",
                "x_label": "City",
                "img_title": "Adoption of Sustainable Building Practices in Cities"
            }
        ],
        "30 - Gaming & Recreation": [
            {
                "bar_data": [250, 220, 210, 180, 170, 160, 150, 140, 130, 120],
                "bar_labels": ["Fortnite", "Minecraft", "Roblox", "League of Legends", "Call of Duty", "PUBG", "Genshin Impact", "Valorant", "Apex Legends", "FIFA"],
                "bar_colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
                "y_label": "Monthly Active Users (Millions)",
                "x_label": "Game",
                "img_title": "Top 10 Games by Monthly Active Users"
            },
            {
                "bar_data": [96.0, 92.3, 90.5, 89.0, 88.2, 86.5, 85.4, 84.6, 83.9, 83.0],
                "bar_labels": ["The Last of Us", "God of War", "Red Dead Redemption 2", "Zelda: Breath of the Wild", "Elden Ring", "Persona 5", "Spider-Man", "Hades", "Ghost of Tsushima", "Hollow Knight"],
                "bar_colors": ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf", "#999999", "#66c2a5"],
                "y_label": "Metacritic Score",
                "x_label": "Game",
                "img_title": "Top Rated Games of the Decade"
            },
            {
                "bar_data": [6000, 5700, 5400, 5300, 5000, 4800, 4600, 4400, 4300, 4200],
                "bar_labels": ["Tetris", "Minecraft", "GTA V", "Wii Sports", "PUBG", "Super Mario Bros.", "Pokemon Red/Blue", "Mario Kart 8", "Wii Fit", "Terraria"],
                "bar_colors": ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#666666", "#1f78b4", "#b2df8a"],
                "y_label": "Global Sales (in 000s)",
                "x_label": "Game",
                "img_title": "Top Selling Video Games Worldwide"
            },
            {
                "bar_data": [100, 95, 90, 88, 85, 82, 80, 77, 75, 73],
                "bar_labels": ["Twitch", "YouTube Gaming", "Facebook Gaming", "Kick", "Trovo", "Steam Broadcast", "DLive", "Nimo TV", "Huya", "Bigo Live"],
                "bar_colors": ["#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a"],
                "y_label": "Streaming Platform Reach (Millions)",
                "x_label": "Platform",
                "img_title": "Top Game Streaming Platforms by Reach"
            },
            {
                "bar_data": [12.5, 10.3, 9.8, 9.2, 8.9, 8.6, 8.0, 7.7, 7.3, 6.9],
                "bar_labels": ["Dungeons & Dragons", "Pathfinder", "Call of Cthulhu", "Warhammer", "Blades in the Dark", "Starfinder", "Shadowrun", "Cyberpunk", "FATE", "GURPS"],
                "bar_colors": ["#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd"],
                "y_label": "Active Players (Millions)",
                "x_label": "TTRPG System",
                "img_title": "Popularity of Tabletop RPG Systems"
            },
            {
                "bar_data": [88, 81, 75, 70, 65, 60, 58, 55, 53, 50],
                "bar_labels": ["Chess", "Poker", "Scrabble", "Backgammon", "Mahjong", "Go", "Monopoly", "Uno", "Risk", "Catan"],
                "bar_colors": ["#ff8c00", "#e9967a", "#8fbc8f", "#483d8b", "#2e8b57", "#d2691e", "#5f9ea0", "#9acd32", "#ff1493", "#00ced1"],
                "y_label": "Global Player Base (Millions)",
                "x_label": "Game",
                "img_title": "Most Played Traditional Board & Card Games"
            },
            {
                "bar_data": [1200, 1100, 1020, 980, 960, 940, 900, 880, 870, 860],
                "bar_labels": ["League of Legends", "Dota 2", "Fortnite", "Valorant", "CS:GO", "PUBG", "Overwatch", "Apex Legends", "Rocket League", "Call of Duty"],
                "bar_colors": ["#ff6347", "#4682b4", "#daa520", "#32cd32", "#ba55d3", "#3cb371", "#b0c4de", "#ff4500", "#2e8b57", "#ff1493"],
                "y_label": "Esports Prize Pool ($ Thousands)",
                "x_label": "Game",
                "img_title": "Top Esports Titles by Prize Pool in 2024"
            },
            {
                "bar_data": [47, 43, 40, 38, 35, 33, 30, 28, 26, 24],
                "bar_labels": ["Candy Crush", "Clash of Clans", "Honor of Kings", "Pokémon Go", "PUBG Mobile", "Genshin Impact", "Roblox Mobile", "Subway Surfers", "Coin Master", "Call of Duty Mobile"],
                "bar_colors": ["#ff7f50", "#6a5acd", "#20b2aa", "#ff69b4", "#cd853f", "#b0e0e6", "#ff4500", "#2e8b57", "#ff1493", "#00ced1"],
                "y_label": "Annual Revenue (Billions USD)",
                "x_label": "Mobile Game",
                "img_title": "Highest Grossing Mobile Games of the Year"
            },
            {
                "bar_data": [60, 58, 55, 52, 50, 48, 46, 44, 43, 42],
                "bar_labels": ["PC", "PlayStation", "Xbox", "Switch", "Mobile", "VR", "Steam Deck", "Browser", "Cloud Gaming", "Arcade"],
                "bar_colors": ["#7fffd4", "#ff69b4", "#cd5c5c", "#ffa500", "#40e0d0", "#9acd32", "#ff4500", "#da70d6", "#7fff00", "#d2691e"],
                "y_label": "Gaming Hours per Week (Millions)",
                "x_label": "Platform",
                "img_title": "Weekly Gaming Hours by Platform"
            },
            {
                "bar_data": [35, 32, 30, 28, 27, 25, 24, 22, 20, 18],
                "bar_labels": ["Adventure", "Shooter", "Puzzle", "Simulation", "Strategy", "Role-playing", "Sports", "Platformer", "Racing", "Fighting"],
                "bar_colors": ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf", "#999999", "#66c2a5"],
                "y_label": "Market Share (%)",
                "x_label": "Game Genre",
                "img_title": "Global Game Genre Market Share (2024)"
            }
        ],
    }
}
#         "1 - Media & Entertainment": [
#             {
#                 "chart_data": {
#                     "Netflix": [2.3, 2.1, 1.9, 2.5, 2.8, 2.6, 3.0, 3.1, 2.7, 2.4, 2.2, 2.0],
#                     "Disney+": [1.7, 1.6, 1.4, 1.8, 2.0, 2.1, 2.2, 2.3, 2.1, 1.9, 1.6, 1.4],
#                     "Amazon Prime Video": [1.9, 2.0, 1.8, 2.1, 2.3, 2.2, 2.5, 2.6, 2.4, 2.0, 1.8, 1.7],
#                     "HBO Max": [1.1, 1.2, 1.0, 1.4, 1.5, 1.6, 1.8, 1.9, 1.7, 1.5, 1.2, 1.0],
#                     "Hulu": [0.9, 1.0, 0.8, 1.1, 1.2, 1.3, 1.5, 1.6, 1.4, 1.1, 1.0, 0.9],
#                     "Apple TV+": [0.8, 0.9, 0.7, 1.0, 1.1, 1.2, 1.3, 1.4, 1.3, 1.0, 0.9, 0.8]
#                 },
#                 "chart_labels": ["Netflix", "Disney+", "Amazon", "HBO Max", "Hulu", "Apple TV+"],
#                 "chart_colors": ["#E50914", "#113CCF", "#00A8E1", "#8E44AD", "#81C784", "#999999"],
#                 "x_label": "Months",
#                 "y_label": "New Subscribers (Millions)",
#                 "img_title": "Monthly Subscriber Growth of Streaming Platforms (2024)"
#             },
#             {
#                 "chart_data": {
#                     "Avatar: The Way of Water": [134, 98, 85, 74, 60, 54, 47, 42, 38, 34, 31, 28],
#                     "Oppenheimer": [82, 70, 65, 60, 54, 49, 43, 39, 34, 30, 28, 25],
#                     "Barbie": [95, 87, 76, 68, 58, 53, 47, 42, 37, 33, 30, 27],
#                     "John Wick 4": [72, 63, 55, 48, 41, 36, 30, 26, 22, 19, 17, 15],
#                     "Spider-Man: Across the Spider-Verse": [89, 80, 74, 68, 60, 53, 45, 40, 35, 30, 28, 25],
#                     "The Super Mario Bros. Movie": [100, 91, 83, 75, 65, 58, 50, 45, 40, 35, 32, 30]
#                 },
#                 "chart_labels": ["Avatar", "Oppenheimer", "Barbie", "John Wick", "Spider-Verse", "Mario"],
#                 "chart_colors": ["#1ABC9C", "#3498DB", "#E91E63", "#FF9800", "#9C27B0", "#4CAF50"],
#                 "x_label": "Weeks Since Release",
#                 "y_label": "Weekly Earnings ($ Million)",
#                 "img_title": "Box Office Earnings Over 12 Weeks"
#             },
#             {
#                 "chart_data": {
#                     "Drama": [1.4, 1.5, 1.6, 1.7, 1.6, 1.8, 1.9, 1.7, 1.6, 1.5, 1.3, 1.2],
#                     "Comedy": [1.3, 1.4, 1.5, 1.6, 1.4, 1.5, 1.6, 1.4, 1.3, 1.2, 1.1, 1.0],
#                     "Sci-Fi": [1.0, 1.1, 1.2, 1.3, 1.2, 1.3, 1.4, 1.2, 1.1, 1.0, 0.9, 0.8],
#                     "Documentary": [0.7, 0.8, 0.9, 1.0, 0.9, 1.0, 1.1, 0.9, 0.8, 0.7, 0.6, 0.5],
#                     "Horror": [0.6, 0.7, 0.8, 0.9, 0.8, 0.9, 1.0, 0.8, 0.7, 0.6, 0.5, 0.4],
#                     "Animation": [0.9, 1.0, 1.1, 1.2, 1.1, 1.3, 1.4, 1.2, 1.1, 1.0, 0.9, 0.8]
#                 },
#                 "chart_labels": ["Drama", "Comedy", "Sci-Fi", "Documentary", "Horror", "Animation"],
#                 "chart_colors": ["#FF7043", "#42A5F5", "#66BB6A", "#AB47BC", "#EF5350", "#FFD54F"],
#                 "x_label": "Month",
#                 "y_label": "Daily Watch Time (Hours)",
#                 "img_title": "Average Daily Viewing Time by Genre (2024)"
#             },
#             {
#                 "chart_data": {
#                     "Spotify": [112, 115, 118, 120, 123, 127, 130, 132, 134, 136, 139, 141],
#                     "Apple Music": [85, 88, 90, 92, 94, 96, 99, 101, 103, 105, 108, 110],
#                     "Amazon Music": [75, 77, 79, 80, 82, 84, 86, 88, 89, 91, 93, 94],
#                     "YouTube Music": [65, 67, 69, 70, 72, 74, 76, 77, 78, 80, 82, 83],
#                     "Deezer": [20, 21, 21, 22, 23, 23, 24, 25, 25, 26, 26, 27],
#                     "Tidal": [15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20]
#                 },
#                 "chart_labels": ["Spotify", "Apple Music", "Amazon Music", "YouTube Music", "Deezer", "Tidal"],
#                 "chart_colors": ["#1DB954", "#FA57C1", "#FF9900", "#FF0000", "#009688", "#3F51B5"],
#                 "x_label": "Month",
#                 "y_label": "Revenue ($ Million)",
#                 "img_title": "Monthly Revenue of Top Music Streaming Services (2024)"
#             },
#             {
#                 "chart_data": {
#                     "The Last of Us": [6.5, 6.8, 7.1, 7.5, 7.8, 8.1, 8.3, 8.2, 8.0, 7.9, 7.7, 7.5],
#                     "Succession": [5.1, 5.3, 5.6, 5.8, 6.0, 6.3, 6.5, 6.4, 6.2, 6.0, 5.9, 5.7],
#                     "Stranger Things": [7.9, 8.2, 8.5, 8.8, 9.1, 9.3, 9.5, 9.4, 9.2, 9.0, 8.8, 8.5],
#                     "Wednesday": [6.2, 6.4, 6.6, 6.9, 7.1, 7.3, 7.5, 7.4, 7.2, 7.0, 6.8, 6.5],
#                     "Ted Lasso": [4.8, 5.0, 5.2, 5.5, 5.7, 5.9, 6.1, 6.0, 5.8, 5.6, 5.4, 5.2],
#                     "The Mandalorian": [6.0, 6.3, 6.5, 6.8, 7.0, 7.2, 7.4, 7.3, 7.1, 6.9, 6.7, 6.5]
#                 },
#                 "chart_labels": ["Last of Us", "Succession", "Stranger Things", "Wednesday", "Ted Lasso", "Mandalorian"],
#                 "chart_colors": ["#607D8B", "#795548", "#3F51B5", "#FF4081", "#FFC107", "#009688"],
#                 "x_label": "Weeks",
#                 "y_label": "Weekly Viewership (Millions)",
#                 "img_title": "TV Show Weekly Viewership Trends (2024)"
#             },
#         ]
#     }
# }

import numpy as np
METADATA_HISTOGRAM = {
    "draw__2_histogram__func_1": {
        "1 - Media & Entertainment": [
            {
                "histogram_data": np.random.normal(90, 10, 100).tolist(),
                "bin_edges": [60, 70, 80, 90, 100, 110, 120],  # 6 bins with clear boundaries
                "x_label": "Movie Runtime (Minutes)",
                "y_label": "Number of Movies",
                "img_title": "Distribution of Movie Runtimes in Top Streaming Services (2024)",
                "chart_color": "#4A90E2",
                "tick_step": 2,  # Show tick every 2 bins
            },
        ]
    }
}


METADATA_SCATTER = {
    "draw__3_scatter__func_1": {
        "1 - Media & Entertainment": [
            {
                "scatter_x_data": [1.2, 2.5, 3.8, 4.1, 5.3, 6.7, 7.2, 8.5, 9.1, 10.4],
                "scatter_y_data": [22.75, 32.43, 33.96, 45.36, 19.32, 38.64, 55.72, 58.91, 40.11, 27.84],
                "scatter_labels": ["Inception", "The Grand Budapest Hotel", "The Matrix", "Spirited Away", "Parasite", "Pulp Fiction", "The Dark Knight", "Titanic", "Interstellar", "The Shawshank Redemption"],
                "scatter_colors": ["#DE7676", "#EEA658", "#FFF46F", "#3DB60D", "#ADCDF6", "#73ECE2", "#BF7023", "#C02222", "#92D610", "#2279E4"],
                "scatter_sizes": [ddd * 100 for ddd in [1.2, 2.5, 3.8, 4.1, 5.3, 6.7, 7.2, 8.5, 9.1, 10.4]],
                "x_label": "Rating Score",
                "y_label": "Annual Box Office Earnings ($ Million)",
                "img_title": "Movie Ratings vs Box Office Earnings",
            },
            {
                "scatter_x_data": [7.8, 8.3, 9.1, 7.2, 6.9, 8.9, 9.3, 6.5, 8.0, 7.5],
                "scatter_y_data": [1200, 1100, 950, 1500, 2000, 800, 1300, 1800, 2200, 1050],
                "scatter_labels": ["Stranger Things", "Breaking Bad", "Game of Thrones", "The Crown", "The Witcher", "Chernobyl", "The Mandalorian", "Emily in Paris", "The Queen's Gambit", "Dark"],
                "scatter_colors": ["#4A90E2", "#50E3C2", "#BD10E0", "#F8E71C", "#D0021B", "#7ED321", "#417505", "#B8E986", "#F5A623", "#9013FE"],
                "scatter_sizes": [ddd * 100 for ddd in [7.8, 8.3, 9.1, 7.2, 6.9, 8.9, 9.3, 6.5, 8.0, 7.5]],
                "x_label": "Average IMDb Rating",
                "y_label": "Total Streaming Hours (Millions)",
                "img_title": "Streaming Popularity vs User Ratings for Top TV Series"
            },
        ],
        "2 - Geography & Demography": [
            {
                "scatter_x_data": [34.5, 36.1, 38.7, 32.2, 35.9, 41.4, 37.6, 39.3, 34.0, 33.1],
                "scatter_y_data": [8.4, 3.9, 2.7, 9.2, 6.7, 1.5, 4.1, 2.3, 7.1, 5.6],
                "scatter_labels": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "San Jose", "Philadelphia", "San Diego", "Dallas", "Austin"],
                "scatter_colors": ["#FF5733", "#33FF57", "#3357FF", "#F4D03F", "#5DADE2", "#D98880", "#58D68D", "#AF7AC5", "#F1948A", "#5B2C6F"],
                "scatter_sizes": [ddd * 10 for ddd in [8.4, 3.9, 2.7, 9.2, 6.7, 1.5, 4.1, 2.3, 7.1, 5.6]],
                "x_label": "Average Age (Years)",
                "y_label": "City Population (Millions)",
                "img_title": "Population vs Average Age Across Major U.S. Cities"
            },
            {
                "scatter_x_data": [464, 153, 36, 276, 421, 240, 119, 540, 207, 347],
                "scatter_y_data": [92.0, 74.3, 83.4, 66.1, 60.2, 81.8, 90.1, 56.5, 88.6, 61.9],
                "scatter_labels": ["India", "USA", "Canada", "UK", "Philippines", "Vietnam", "Brazil", "Bangladesh", "South Korea", "Germany"],
                "scatter_colors": ["#EB984E", "#58D68D", "#5DADE2", "#AF7AC5", "#D98880", "#73C6B6", "#F4D03F", "#CD6155", "#2980B9", "#F5B041"],
                "scatter_sizes": [ddd * 0.8 for ddd in [464, 153, 36, 276, 421, 240, 119, 540, 207, 347]],
                "x_label": "Population Density (People/km²)",
                "y_label": "Urbanization Rate (%)",
                "img_title": "Density vs Urbanization Across Countries"
            },
        ],
        "3 - Education & Academia": [
            {
                "scatter_x_data": [16, 15, 14, 11, 13, 10, 12, 17, 9, 18],
                "scatter_y_data": [85, 91, 95, 93, 80, 96, 77, 69, 82, 68],
                "scatter_labels": ["Harvard", "MIT", "Stanford", "Yale", "UCLA", "UC Berkeley", "Princeton", "Columbia", "Oxford", "Cambridge"],
                "scatter_colors": ["#1F618D", "#117A65", "#AF601A", "#76448A", "#CA6F1E", "#F1C40F", "#A569BD", "#52BE80", "#EC7063", "#2874A6"],
                "scatter_sizes": [ddd * 15 for ddd in [16, 15, 14, 11, 13, 10, 12, 17, 9, 18]],
                "x_label": "Student-to-Teacher Ratio",
                "y_label": "Graduation Rate (%)",
                "img_title": "Impact of Class Size on Graduation Rates"
            },
            {
                "scatter_x_data": [200, 180, 210, 190, 160, 220, 150, 130, 170, 140],
                "scatter_y_data": [8000, 6300, 7800, 5000, 7100, 8200, 6600, 5400, 7500, 8500],
                "scatter_labels": ["MIT", "Stanford", "Harvard", "Caltech", "ETH Zurich", "Tokyo University", "Oxford", "Cambridge", "Tsinghua", "Toronto"],
                "scatter_colors": ["#154360", "#1E8449", "#7D6608", "#943126", "#1ABC9C", "#E67E22", "#2980B9", "#9B59B6", "#F39C12", "#2ECC71"],
                "scatter_sizes": [ddd * 4 for ddd in [200, 180, 210, 190, 160, 220, 150, 130, 170, 140]],
                "x_label": "Annual Research Funding ($ Million)",
                "y_label": "Academic Publications per Year",
                "img_title": "Research Output vs Funding Across Universities"
            },
        ],
        "4 - Business & Industry": [
            {
                "scatter_x_data": [1, 10, 5, 2, 3, 8, 9, 4, 6, 7],
                "scatter_y_data": [0.3, 1.1, 2.4, 4.0, 5.3, 0.8, 6.1, 1.9, 3.1, 7.0],
                "scatter_labels": ["Startly", "FinNxt", "EduLift", "QuickCart", "HealthIO", "GreenGrid", "DataForge", "AutoBotics", "CleanAirTech", "AgriWave"],
                "scatter_colors": ["#F1948A", "#82E0AA", "#5DADE2", "#F8C471", "#BB8FCE", "#73C6B6", "#F0B27A", "#5499C7", "#45B39D", "#AF7AC5"],
                "scatter_sizes": [ddd * 100 for ddd in [0.3, 1.1, 2.4, 4.0, 5.3, 0.8, 6.1, 1.9, 3.1, 7.0]],
                "x_label": "Years Since Founding",
                "y_label": "Annual Revenue ($ Million)",
                "img_title": "Startup Age vs Annual Revenue"
            },
            {
                "scatter_x_data": [500, 800, 850, 600, 750, 400, 200, 300, 150, 900],
                "scatter_y_data": [50, 1000, 120, 250, 90, 350, 700, 850, 600, 900],
                "scatter_labels": ["TechNova", "InnoWare", "NeoCloud", "Medilink", "EcoSys", "TransEdge", "UrbanLoop", "FoodChain", "BitBay", "AutoNest"],
                "scatter_colors": ["#2F86C1", "#28B463", "#CF4335", "#F1C40F", "#DB59B6", "#A980B9", "#F39C12", "#1ABC9C", "#E67E22", "#FD3555"],
                "scatter_sizes": [ddd * 1.2 for ddd in [50, 1000, 120, 250, 90, 350, 700, 850, 600, 900]],
                "x_label": "Employee Count",
                "y_label": "Company Valuation ($ Million)",
                "img_title": "Employees vs Company Valuation"
            },
        ],
        "5 - Major & Course": [
            {
                "scatter_x_data": [35, 45, 38, 42, 28, 30, 32, 40, 25, 36],
                "scatter_y_data": [3.6, 3.9, 3.7, 3.3, 3.8, 3.2, 3.4, 3.8, 3.1, 3.5],
                "scatter_labels": ["Engineering", "Physics", "Sociology", "Economics", "Mathematics", "Biology", "History", "Computer Science", "Art", "Chemistry"],
                "scatter_colors": ["#1F618D", "#196F3D", "#943126", "#76448A", "#117A65", "#B9770E", "#D98880", "#2980B9", "#F4D03F", "#C39BD3"],
                "scatter_sizes": [ddd * 30 for ddd in [35, 45, 38, 42, 28, 30, 32, 40, 25, 36]],
                "x_label": "Average Study Hours/Week",
                "y_label": "GPA",
                "img_title": "Study Time vs GPA Across University Majors"
            },
            {
                "scatter_x_data": [8.5, 9.0, 7.5, 6.0, 6.5, 8.2, 9.3, 9.5, 8.0, 7.0],
                "scatter_y_data": [12, 15, 9, 7, 20, 13, 8, 6, 11, 18],
                "scatter_labels": ["Calculus", "Organic Chemistry", "Philosophy", "Business 101", "Quantum Physics", "Algorithms", "Literature", "Psychology", "Statistics", "Thermodynamics"],
                "scatter_colors": ["#F1948A", "#85C1E9", "#BB8FCE", "#82E0AA", "#F8C471", "#E67E22", "#A569BD", "#2ECC71", "#EC7063", "#5DADE2"],
                "scatter_sizes": [ddd * 100 for ddd in [12, 15, 9, 7, 20, 13, 8, 6, 11, 18]],
                "x_label": "Course Difficulty (1-10)",
                "y_label": "Dropout Rate (%)",
                "img_title": "Difficulty vs Dropout Rate in University Courses"
            },
        ],
        "6 - Animal & Zoology": [
            {
                "scatter_x_data": [600, 25, 190, 220, 35, 30, 50, 10, 12, 6],
                "scatter_y_data": [45, 15, 70, 60, 30, 3, 20, 5, 12, 8],
                "scatter_labels": ["Lion", "Tiger", "Mouse", "Dog", "Rabbit", "Cat", "Fox", "Elephant", "Goat", "Kangaroo"],
                "scatter_colors": ["#F5B041", "#E67E22", "#BB8FCE", "#58D68D", "#F1948A", "#6EADE2", "#BF7AC5", "#FCC471", "#A4BE80", "#DE8880"],
                "scatter_sizes": [ddd * 8 for ddd in [600, 25, 190, 220, 35, 30, 50, 10, 12, 6]],
                "x_label": "Average Weight (kg)",
                "y_label": "Lifespan (Years)",
                "img_title": "Animal Size vs Lifespan"
            },
            {
                "scatter_x_data": [120, 110, 70, 80, 60, 25, 50, 40, 90, 55],
                "scatter_y_data": [0.015, 0.018, 0.010, 0.012, 0.011, 0.035, 0.030, 0.028, 0.014, 0.032],
                "scatter_labels": ["Cheetah", "Pronghorn", "Lion", "Gazelle", "Greyhound", "Dolphin", "Chimpanzee", "Crow", "Ostrich", "Octopus"],
                "scatter_colors": ["#F8C471", "#A569BD", "#2980B9", "#F1948A", "#58D68D", "#D98880", "#AF7AC5", "#5DADE2", "#F39C12", "#7DCEA0"],
                "scatter_sizes": [ddd * 30000 for ddd in [0.015, 0.018, 0.010, 0.012, 0.011, 0.035, 0.030, 0.028, 0.014, 0.032]],
                "x_label": "Top Speed (km/h)",
                "y_label": "Brain-to-Body Mass Ratio",
                "img_title": "Animal Speed vs Intelligence Indicator"
            },
        ],
        "7 - Plant & Botany": [
            {
                "scatter_x_data": [2.3, 4.5, 5.1, 7, 16, 15, 5, 3.6, 10, 3.8],
                "scatter_y_data": [10, 12, 7, 15, 17, 28, 14, 9, 16, 23],
                "scatter_labels": ["Tulip", "Rose", "Oak Tree", "Sunflower", "Basil", "Maple Tree", "Lavender", "Moss", "Palm", "Cedar"],
                "scatter_colors": ["#7DCEA0", "#F39C12", "#5DADE2", "#BB8FCE", "#E67E22", "#2980B9", "#58D68D", "#F5B041", "#D98880", "#AF7AC5"],
                "scatter_sizes": [ddd * 100 for ddd in [2.3, 4.5, 5.1, 7, 16, 15, 5, 3.6, 10, 3.8]],
                "x_label": "Plant Height (Meters)",
                "y_label": "Photosynthesis Rate (µmol CO₂/m²/s)",
                "img_title": "Plant Size vs Photosynthesis Efficiency"
            },
            {
                "scatter_x_data": [15, 5, 8, 3, 12, 2, 7, 6, 4, 10],
                "scatter_y_data": [7, 12, 6, 15, 8, 18, 9, 13, 14, 11],
                "scatter_labels": ["Dandelion", "Apple", "Maple", "Pea", "Pine", "Bean", "Acacia", "Coconut", "Cherry", "Wheat"],
                "scatter_colors": ["#F1948A", "#A569BD", "#52BE80", "#F8C471", "#5DADE2", "#D98880", "#F39C12", "#58D68D", "#BB8FCE", "#2980B9"],
                "scatter_sizes": [ddd * 75 for ddd in [15, 5, 8, 3, 12, 2, 7, 6, 4, 10]],
                "x_label": "Seed Dispersal Distance (Meters)",
                "y_label": "Germination Time (Days)",
                "img_title": "Seed Travel vs Germination Time"
            },
        ],
        "8 - Biology & Chemistry": [
            {
                "scatter_x_data": [18, 44, 28, 60, 98, 120, 16, 76, 142, 190],
                "scatter_y_data": [0.8, 2.3, 1.4, 3.1, 2.8, 4.2, 0.5, 3.0, 5.6, 6.8],
                "scatter_labels": ["Water", "CO2", "N2", "Ethanol", "H2SO4", "Glucose", "Methane", "Benzene", "Caffeine", "Cholesterol"],
                "scatter_colors": ["#58D68D", "#F39C12", "#2980B9", "#BB8FCE", "#F5B041", "#D98880", "#A569BD", "#5DADE2", "#E67E22", "#AF7AC5"],
                "scatter_sizes": [ddd * 100 for ddd in [0.8, 2.3, 1.4, 3.1, 2.8, 4.2, 0.5, 3.0, 5.6, 6.8]],
                "x_label": "Molecular Weight (g/mol)",
                "y_label": "Reaction Time (Seconds)",
                "img_title": "Molecule Size vs Reaction Time"
            },
            {
                "scatter_x_data": [1, 3, 5, 7, 9, 11, 13, 2, 4, 6],
                "scatter_y_data": [0.9, 4.5, 6.1, 2.5, 4.8, 7.4, 6.9, 3.2, 4.9, 5.3],
                "scatter_labels": ["HCl", "Vinegar", "Black Coffee", "Pure Water", "Baking Soda", "Ammonia", "Bleach", "Lemon Juice", "Milk", "Sea Water"],
                "scatter_colors": ["#F8C471", "#2980B9", "#D98880", "#52BE80", "#AF7AC5", "#E67E22", "#5DADE2", "#AA8395", "#FA69BD", "#F39C12"],
                "scatter_sizes": [ddd * 80 for ddd in [0.9, 4.5, 6.1, 2.5, 4.8, 7.4, 6.9, 3.2, 4.9, 5.3]],
                "x_label": "pH Level",
                "y_label": "Conductivity (mS/cm)",
                "img_title": "pH vs Electrical Conductivity of Substances"
            },
        ],
        "9 - Food & Nutrition": [
            {
                "scatter_x_data": [250, 150, 100, 180, 75, 350, 90, 300, 220, 400],
                "scatter_y_data": [18, 30, 15, 20, 5, 3, 1, 25, 2, 27],
                "scatter_labels": ["Chicken Breast", "Apple", "Carrot", "Banana", "Steak", "Egg", "Salmon", "Tofu", "Cucumber", "Pork"],
                "scatter_colors": ["#F1948A", "#58D68D", "#5DADE2", "#F5B041", "#AF7AC5", "#F8C471", "#D98880", "#A569BD", "#2980B9", "#F39C12"],
                "scatter_sizes": [ddd * 2 for ddd in [250, 150, 100, 180, 75, 350, 90, 300, 220, 400]],
                "x_label": "Calories",
                "y_label": "Protein Content (g)",
                "img_title": "Calories vs Protein in Foods"
            },
            {
                "scatter_x_data": [5, 38, 33, 45, 30, 19, 25, 10, 20, 15],
                "scatter_y_data": [85, 65, 78, 95, 70, 40, 30, 90, 88, 55],
                "scatter_labels": ["Soda", "Yogurt", "Cake", "Orange", "Nuts", "Candy", "Ice Cream", "White Bread", "Grapes", "Milk"],
                "scatter_colors": ["#F5B041", "#BB8FCE", "#2980B9", "#58D68D", "#F39C12", "#AF7AC5", "#E67E22", "#5DADE2", "#F1948A", "#D98880"],
                "scatter_sizes": [ddd * 40 for ddd in [5, 38, 33, 45, 30, 19, 25, 10, 20, 15]],
                "x_label": "Sugar Content (g per serving)",
                "y_label": "Glycemic Index",
                "img_title": "Sugar vs Glycemic Index of Foods"
            },
        ],
        "10 - Space & Astronomy": [
            {
                "scatter_x_data": [0.55, 0.815, 1.0, 0.107, 17.8, 5.2, 10.5, 15.1, 0.02, 0.12],
                "scatter_y_data": [9388, 18225, 12365, 7687, 14333, 10759, 17687, 20190, 18727, 32248],
                "scatter_labels": ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Moon", "Pluto"],
                "scatter_colors": ["#F39C12", "#58D68D", "#5DADE2", "#AF7AC5", "#F1948A", "#BB8FCE", "#E67E22", "#2980B9", "#D98880", "#F5B041"],
                "scatter_sizes": [ddd * 200 for ddd in [0.055, 0.815, 1.0, 0.107, 317.8, 95.2, 14.5, 17.1, 0.002, 0.012]],
                "x_label": "Mass (Relative to Earth)",
                "y_label": "Orbital Period (Days)",
                "img_title": "Planetary Mass vs Orbital Period"
            },
            {
                "scatter_x_data": [3000, 4500, 5800, 7500, 10000, 15000, 20000, 24000, 6000, 9000],
                "scatter_y_data": [4.0, 40.0, 55.0, 12.0, 25.0, 10.0, 50.0, 100.0, 32, 75],
                "scatter_labels": ["M-type", "K-type", "G-type (Sun)", "F-type", "A-type", "B-type", "O-type", "Blue Giant", "Sun-like", "F5 Star"],
                "scatter_colors": ["#F5B041", "#F1948A", "#58D68D", "#AF7AC5", "#E67E22", "#5DADE2", "#2980B9", "#BB8FCE", "#F39C12", "#D98880"],
                "scatter_sizes": [ddd * 10 for ddd in [4.0, 40.0, 55.0, 12.0, 25.0, 10.0, 50.0, 100.0, 12, 65]],
                "x_label": "Temperature (Kelvin)",
                "y_label": "Luminosity (Relative to Sun)",
                "img_title": "Star Temperature vs Luminosity"
            },
        ],
        "11 - Sale & Merchandise": [
            {
                "scatter_x_data": [15, 25, 10, 40, 100, 80, 5, 60, 30, 50],
                "scatter_y_data": [1200, 950, 3000, 400, 150, 230, 5200, 310, 750, 800],
                "scatter_labels": ["T-shirt", "Jeans", "Notebook", "Backpack", "Smartphone", "Tablet", "Pen", "Headphones", "Shoes", "Watch"],
                "scatter_colors": ["#F39C12", "#2980B9", "#58D68D", "#AF7AC5", "#F1948A", "#E67E22", "#5DADE2", "#BB8FCE", "#D98880", "#F5B041"],
                "scatter_sizes": [ddd * 0.3 for ddd in [1200, 950, 3000, 400, 150, 230, 5200, 310, 750, 800]],
                "x_label": "Price ($)",
                "y_label": "Units Sold (Monthly)",
                "img_title": "Product Price vs Sales Volume"
            },
            {
                "scatter_x_data": [1.6, 3.8, 2.2, 5.9, 3.5, 4.1, 2.8, 3.9, 4.7, 6.3],
                "scatter_y_data": [2, 5, 3, 1, 8, 4, 12, 6, 2, 3],
                "scatter_labels": ["Headphones", "Shoes", "Keyboard", "Laptop", "Dress", "Speaker", "Blender", "Mouse", "Monitor", "Webcam"],
                "scatter_colors": ["#AF7AC5", "#E67E22", "#58D68D", "#AB9375", "#F5B041", "#2980B9", "#D98880", "#5DADE2", "#BB8FCE", "#932012"],
                "scatter_sizes": [ddd * 100 for ddd in [2, 5, 3, 1, 8, 4, 12, 6, 2, 3]],
                "x_label": "Average User Rating (5-star scale)",
                "y_label": "Return Rate (%)",
                "img_title": "Customer Satisfaction vs Product Returns"
            },
        ],
        "12 - Market & Economy": [
            {
                "scatter_x_data": [21.4, 14.7, 5.2, 3.8, 2.9, 1.6, 2.2, 4.0, 0.9, 1.3],
                "scatter_y_data": [3.5, 5.2, 4.0, 6.8, 7.1, 3.1, 4.4, 5.9, 6.3, 4.8],
                "scatter_labels": ["USA", "China", "Japan", "Germany", "India", "Australia", "Brazil", "UK", "South Africa", "Canada"],
                "scatter_colors": ["#F1948A", "#58D68D", "#AF7AC5", "#5DADE2", "#F5B041", "#2980B9", "#E67E22", "#BB8FCE", "#D98880", "#F39C12"],
                "scatter_sizes": [ddd * 100 for ddd in [3.5, 5.2, 4.0, 6.8, 7.1, 3.1, 4.4, 5.9, 6.3, 4.8]],
                "x_label": "GDP (Trillion USD)",
                "y_label": "Unemployment Rate (%)",
                "img_title": "GDP vs Unemployment Rate by Country"
            },
            {
                "scatter_x_data": [2.5, 3.8, 6.1, 2.2, 5.5, 8.9, 2.1, 3.5, 6.7, 5.4],
                "scatter_y_data": [2500, 1700, 3200, 1900, 1100, 2700, 1500, 3400, 1600, 2000],
                "scatter_labels": ["Apple", "Microsoft", "Tesla", "Amazon", "NVIDIA", "Meta", "Alphabet", "Netflix", "Intel", "AMD"],
                "scatter_colors": ["#AF7AC5", "#960412", "#5DADE2", "#F1948A", "#2980B9", "#F5B041", "#E67E22", "#58D68D", "#D98880", "#BB8FCE"],
                "scatter_sizes": [ddd * 0.5 for ddd in [2500, 1700, 3200, 1900, 1100, 2700, 1500, 3400, 1600, 2000]],
                "x_label": "Stock Price Volatility (%)",
                "y_label": "Market Cap (Billion USD)",
                "img_title": "Volatility vs Market Capitalization"
            },
        ],
        "13 - Sports & Athletics": [
            {
                "scatter_x_data": [1.85, 2.01, 1.93, 2.11, 1.88, 1.97, 2.06, 2.03, 1.91, 2.09],
                "scatter_y_data": [42, 38, 40, 66, 44, 59, 65, 77, 43, 34],
                "scatter_labels": ["Curry", "LeBron", "Harden", "Jokic", "Lillard", "Butler", "Embiid", "Tatum", "Morant", "Giannis"],
                "scatter_colors": ["#F39C12", "#AF7AC5", "#2980B9", "#F1948A", "#58D68D", "#E67E22", "#5DADE2", "#F5B041", "#BB8FCE", "#D98880"],
                "scatter_sizes": [ddd * 10 for ddd in [42, 38, 40, 66, 44, 59, 65, 77, 43, 34]],
                "x_label": "Height (Meters)",
                "y_label": "Vertical Jump (Inches)",
                "img_title": "Height vs Vertical Leap in Basketball"
            },
            {
                "scatter_x_data": [18, 21, 24, 27, 30, 33, 36, 39, 42, 45],
                "scatter_y_data": [10.1, 29.8, 10.0, 30.2, 20.3, 15.5, 22.6, 16.9, 21.2, 11.5],
                "scatter_labels": ["Runner1", "Runner2", "Runner3", "Runner4", "Runner5", "Runner6", "Runner7", "Runner8", "Runner9", "Runner10"],
                "scatter_colors": ["#AF7AC5", "#F5B041", "#F1948A", "#58D68D", "#5DADE2", "#2980B9", "#D98880", "#E67E22", "#BB8FCE", "#F39C12"],
                "scatter_sizes": [ddd * 20 for ddd in [10.1, 9.8, 10.0, 30.2, 20.3, 15.5, 22.6, 16.9, 21.2, 11.5]],
                "x_label": "Athlete Age (Years)",
                "y_label": "100m Sprint Time (Seconds)",
                "img_title": "Age vs Sprint Performance in Athletics"
            },
        ],
        "14 - Computing & Technology": [
            {
                "scatter_x_data": [2.0, 2.5, 3.0, 3.5, 4.0, 2.8, 3.2, 4.2, 3.6, 3.9],
                "scatter_y_data": [35, 50, 65, 80, 100, 55, 70, 110, 85, 95],
                "scatter_labels": ["Intel i3", "Intel i5", "Intel i7", "Intel i9", "AMD Ryzen 9", "AMD Ryzen 5", "Apple M1", "Apple M2", "Xeon", "Threadripper"],
                "scatter_colors": ["#F5B041", "#2980B9", "#AF7AC5", "#58D68D", "#F1948A", "#5DADE2", "#BB8FCE", "#E67E22", "#D98880", "#F39C12"],
                "scatter_sizes": [ddd * 1.5 for ddd in [35, 50, 65, 80, 100, 55, 70, 110, 85, 95]],
                "x_label": "Clock Speed (GHz)",
                "y_label": "Power Consumption (W)",
                "img_title": "Processor Performance vs Power Usage"
            },
            {
                "scatter_x_data": [25, 40, 35, 60, 75, 30, 50, 80, 55, 65],
                "scatter_y_data": [200, 850, 350, 500, 650, 480, 450, 700, 580, 750],
                "scatter_labels": ["Instagram", "TikTok", "WhatsApp", "YouTube", "Snapchat", "Zoom", "Spotify", "Facebook", "Telegram", "X (Twitter)"],
                "scatter_colors": ["#58D68D", "#2980B9", "#AF7AC5", "#F5B041", "#F1948A", "#907263", "#BB8FCE", "#5DADE2", "#D98880", "#F39C12"],
                "scatter_sizes": [ddd * 0.6 for ddd in [200, 850, 300, 500, 650, 280, 450, 700, 520, 600]],
                "x_label": "App Size (MB)",
                "y_label": "Downloads (Millions)",
                "img_title": "App Size vs Popularity"
            },
        ],
        "15 - Health & Medicine": [
            {
                "scatter_x_data": [18, 22, 25, 28, 30, 32, 34, 36, 38, 40],
                "scatter_y_data": [110, 215, 320, 225, 430, 135, 240, 145, 350, 155],
                "scatter_labels": ["Patient A", "Patient B", "Patient C", "Patient D", "Patient E", "Patient F", "Patient G", "Patient H", "Patient I", "Patient J"],
                "scatter_colors": ["#F5B041", "#2980B9", "#BB8FCE", "#AF7AC5", "#F39C12", "#E67E22", "#5DADE2", "#58D68D", "#D98880", "#F1948A"],
                "scatter_sizes": [ddd * 1.2 for ddd in [110, 215, 320, 225, 430, 135, 240, 145, 350, 155]],
                "x_label": "BMI",
                "y_label": "Systolic Blood Pressure (mmHg)",
                "img_title": "BMI vs Blood Pressure in Patients"
            },
            {
                "scatter_x_data": [50, 75, 100, 60, 90, 80, 110, 95, 70, 65],
                "scatter_y_data": [12, 10, 17, 16, 9, 6, 7, 8, 13, 11],
                "scatter_labels": ["Drug A", "Drug B", "Drug C", "Drug D", "Drug E", "Drug F", "Drug G", "Drug H", "Drug I", "Drug J"],
                "scatter_colors": ["#58D68D", "#AF7AC5", "#F1948A", "#2980B9", "#F5B041", "#E67E22", "#D98880", "#5DADE2", "#920573", "#BB8FCE"],
                "scatter_sizes": [ddd * 8 for ddd in [12, 10, 17, 16, 9, 6, 7, 8, 13, 11]],
                "x_label": "Dosage (mg)",
                "y_label": "Recovery Time (Days)",
                "img_title": "Medication Dose vs Recovery Time"
            },
        ],
        "16 - Energy & Environment": [
            {
                "scatter_x_data": [450, 800, 700, 900, 600, 500, 750, 950, 680, 620],
                "scatter_y_data": [200, 350, 380, 200, 280, 320, 130, 420, 290, 170],
                "scatter_labels": ["USA", "China", "India", "Russia", "Japan", "Germany", "Canada", "Brazil", "UK", "France"],
                "scatter_colors": ["#2ECC71", "#C7AB60", "#3498DB", "#1F618D", "#F39C12", "#D35400", "#9B59B6", "#8E44AD", "#E74C3C", "#922B21"],
                "scatter_sizes": [ddd * 0.5 for ddd in [200, 350, 380, 200, 280, 320, 130, 420, 290, 170]],
                "x_label": "Energy Consumption (TWh)",
                "y_label": "CO₂ Emissions (Mt)",
                "img_title": "Energy Use vs CO₂ Emissions by Country"
            },
            {
                "scatter_x_data": [20, 25, 40, 55, 30, 45, 35, 60, 50, 65],
                "scatter_y_data": [12, 18, 15, 17, 23, 25, 20, 14, 16, 26],
                "scatter_labels": ["Sweden", "Germany", "Spain", "Denmark", "Portugal", "USA", "UK", "France", "Japan", "Italy"],
                "scatter_colors": ["#F1C40F", "#B7950B", "#1ABC9C", "#117A65", "#5DADE2", "#21618C", "#EC7063", "#943126", "#BB8FCE", "#76448A"],
                "scatter_sizes": [ddd * 60 for ddd in [12, 18, 15, 17, 23, 25, 20, 14, 16, 26]],
                "x_label": "Renewable Energy Share (%)",
                "y_label": "Electricity Cost ($/kWh)",
                "img_title": "Renewables vs Electricity Cost"
            },
        ],
        "17 - Travel & Expedition": [
            {
                "scatter_x_data": [500, 800, 1500, 2000, 2500, 1000, 3000, 4000, 1200, 1800],
                "scatter_y_data": [120, 400, 350, 150, 700, 380, 740, 850, 230, 580],
                "scatter_labels": ["NY-Boston", "LA-SF", "Chicago-Dallas", "Miami-Toronto", "NY-LA", "Paris-Berlin", "London-Dubai", "Tokyo-LA", "Rome-Athens", "Beijing-Singapore"],
                "scatter_colors": ["#F1948A", "#922B21", "#7FB3D5", "#1B4F72", "#58D68D", "#1E8449", "#F5B041", "#A04000", "#BB8FCE", "#6C3483"],
                "scatter_sizes": [ddd * 0.5 for ddd in [120, 400, 350, 150, 700, 380, 740, 850, 230, 580]],
                "x_label": "Flight Distance (km)",
                "y_label": "Ticket Price ($)",
                "img_title": "Flight Distance vs Cost"
            },
            {
                "scatter_x_data": [5, 8, 10, 7, 6, 9, 4, 10, 3, 12],
                "scatter_y_data": [3, 15, 17, 24, 13, 6, 2, 8, 11, 9],
                "scatter_labels": ["Trek A", "Trek B", "Climb C", "Hike D", "Trip E", "Trail F", "Route G", "Journey H", "Expedition I", "Trek J"],
                "scatter_colors": ["#27AE60", "#145A32", "#2980B9", "#1F618D", "#E67E22", "#BA4A00", "#8E44AD", "#512E5F", "#F7DC6F", "#B7950B"],
                "scatter_sizes": [ddd * 40 for ddd in [3, 15, 17, 24, 13, 6, 2, 8, 11, 9]],
                "x_label": "Backpack Weight (kg)",
                "y_label": "Trip Duration (Days)",
                "img_title": "Pack Load vs Expedition Time"
            },
        ],
        "18 - Arts & Culture": [
            {
                "scatter_x_data": [1000, 2500, 1800, 3200, 1500, 1200, 1800, 2100, 2300, 2100],
                "scatter_y_data": [9.2, 5.5, 4, 6, 7.3, 5.5, 8.2, 6.8, 4.5, 5.7],
                "scatter_labels": ["Louvre", "Metropolitan", "British Museum", "Vatican", "Getty", "Rijksmuseum", "Uffizi", "Prado", "Smithsonian", "Hermitage"],
                "scatter_colors": ["#F39C12", "#B9770E", "#58D68D", "#1E8449", "#5DADE2", "#1A5276", "#D98880", "#922B21", "#BB8FCE", "#6C3483"],
                "scatter_sizes": [ddd * 100 for ddd in [9.2, 5.5, 4, 6, 7.3, 5.5, 8.2, 6.8, 4.5, 5.7]],
                "x_label": "Annual Visitors (Thousands)",
                "y_label": "Funding (Million USD)",
                "img_title": "Museum Visitors vs Funding"
            },
            {
                "scatter_x_data": [320, 200, 450, 600, 150, 500, 380, 270, 420, 310],
                "scatter_y_data": [80, 60, 120, 95, 55, 48, 78, 65, 85, 95],
                "scatter_labels": ["1984", "The Alchemist", "Harry Potter", "LOTR", "Animal Farm", "The Hobbit", "Dune", "The Giver", "Pride & Prejudice", "To Kill a Mockingbird"],
                "scatter_colors": ["#117A65", "#27AE60", "#3498DB", "#1F618D", "#E74C3C", "#943126", "#BB8FCE", "#6C3483", "#F1C40F", "#B7950B"],
                "scatter_sizes": [ddd * 3 for ddd in [80, 60, 120, 95, 55, 48, 78, 65, 85, 95]],
                "x_label": "Book Length (Pages)",
                "y_label": "Popularity Index",
                "img_title": "Book Length vs Popularity"
            },
        ],
        "19 - Communication & Collaboration": [
            {
                "scatter_x_data": [15, 30, 65, 35, 70, 60, 90, 20, 50, 80],
                "scatter_y_data": [7.8, 8.0, 9.5, 6.8, 7.2, 6.5, 6.0, 5.0, 5.5, 4.8],
                "scatter_labels": ["Team A", "Team B", "Team C", "Team D", "Team E", "Team F", "Team G", "Team H", "Team I", "Team J"],
                "scatter_colors": ["#5DADE2", "#154360", "#27AE60", "#145A32", "#E67E22", "#943126", "#BB8FCE", "#512E5F", "#F4D03F", "#B7950B"],
                "scatter_sizes": [ddd * 100 for ddd in [7.8, 8.0, 9.5, 6.8, 7.2, 6.5, 6.0, 5.0, 5.5, 4.8]],
                "x_label": "Meeting Duration (Minutes)",
                "y_label": "Satisfaction Score",
                "img_title": "Meeting Time vs Team Satisfaction"
            },
            {
                "scatter_x_data": [10, 20, 12,  5, 15, 25, 30, 18, 7, 22],
                "scatter_y_data": [2.5, 1.8, 3.2, 2.4, 1.9, 3.0, 2.0, 1.5, 1.2, 1.7],
                "scatter_labels": ["HR", "Marketing", "Sales", "IT", "Finance", "Legal", "Admin", "Support", "Design", "R&D"],
                "scatter_colors": ["#F5B041", "#A04000", "#1ABC9C", "#117864", "#5DADE2", "#154360", "#EC7063", "#922B21", "#BB8FCE", "#6C3483"],
                "scatter_sizes": [ddd * 200 for ddd in [2.5, 1.8, 3.2, 2.4, 1.9, 3.0, 2.0, 1.5, 1.2, 1.7]],
                "x_label": "Emails Sent Daily",
                "y_label": "Avg. Response Time (Hours)",
                "img_title": "Email Frequency vs Response Delay"
            },
        ],
        "20 - Language & Linguistics": [
            {
                "scatter_x_data": [1100, 920, 550, 310, 280, 210, 150, 430, 90, 80],
                "scatter_y_data": [2, 3, 5, 8, 9, 10, 7.5, 4, 6, 3.5],
                "scatter_labels": ["English", "Mandarin", "Spanish", "Russian", "Arabic", "Hindi", "Japanese", "Korean", "Turkish", "Hungarian"],
                "scatter_colors": ["#2ECC71", "#1E8449", "#5DADE2", "#1B4F72", "#F39C12", "#B9770E", "#BB8FCE", "#6C3483", "#E74C3C", "#922B21"],
                "scatter_sizes": [ddd * 200 for ddd in [2, 3, 5, 8, 9, 10, 7.5, 4, 6, 3.5]],
                "x_label": "Speakers (Millions)",
                "y_label": "Language Difficulty (1-10)",
                "img_title": "Language Popularity vs Difficulty"
            },
            {
                "scatter_x_data": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                "scatter_y_data": [1000, 300, 200, 850, 500, 720, 600, 400, 120, 80],
                "scatter_labels": ["a", "the", "this", "which", "before", "because", "although", "whenever", "notwithstanding", "nevertheless"],
                "scatter_colors": ["#58D68D", "#1E8449", "#5DADE2", "#154360", "#F4D03F", "#B7950B", "#E67E22", "#A04000", "#BB8FCE", "#6C3483"],
                "scatter_sizes": [ddd * 1 for ddd in [1000, 300, 200, 850, 500, 720, 600, 400, 120, 80]],
                "x_label": "Word Length (Characters)",
                "y_label": "Frequency (per million words)",
                "img_title": "Word Length vs Usage Frequency"
            },
        ],
        "21 - History & Archaeology": [
            {
                "scatter_x_data": [500, 2000, 1200, 300, 800, 1500, 2500, 100, 1800, 2200],
                "scatter_y_data": [150, 80, 200, 180, 120, 220, 60, 240, 90, 70],
                "scatter_labels": ["Göbekli Tepe", "Stonehenge", "Pyramids of Giza", "Mohenjo-daro", "Machu Picchu", "Pompeii", "Angkor Wat", "Great Zimbabwe", "Petra", "Mesa Verde"],
                "scatter_colors": ["#2ECC71", "#27AE60", "#3498DB", "#1F618D", "#F39C12", "#D35400", "#9B59B6", "#8E44AD", "#E74C3C", "#922B21"],
                "scatter_sizes": [ddd * 3 for ddd in [150, 80, 200, 180, 120, 220, 60, 240, 90, 70]],
                "x_label": "Site Age (Years)",
                "y_label": "Annual Visitors (Thousands)",
                "img_title": "Historical Site Age vs Popularity"
            },
            {
                "scatter_x_data": [2, 5, 8, 1.5, 10, 3, 7, 12, 6, 9],
                "scatter_y_data": [300, 450, 120, 500, 100, 350, 230, 80, 400, 150],
                "scatter_labels": ["Luxor (Egypt)", "Delphi (Greece)", "Teotihuacan (Mexico)", "Knossos (Crete)", "Çatalhöyük (Turkey)", "Troy (Turkey)", "Herculaneum (Italy)", "Jericho (Palestine)", "Harappa (Pakistan)", "Ur (Iraq)"],
                "scatter_colors": ["#F1C40F", "#B7950B", "#1ABC9C", "#117A65", "#5DADE2", "#21618C", "#EC7063", "#943126", "#BB8FCE", "#76448A"],
                "scatter_sizes": [ddd * 2 for ddd in [300, 450, 120, 500, 100, 350, 230, 80, 400, 150]],
                "x_label": "Excavation Depth (m)",
                "y_label": "Artifacts Found",
                "img_title": "Dig Depth vs Artifact Count"
            },
        ],
        "22 - Weather & Climate": [
            {
                "scatter_x_data": [500, 1200, 200, 750, 1500, 300, 900, 450, 1100, 650],
                "scatter_y_data": [23, 10, 15, 5, 12, 8, 26, 12, 39, 24],
                "scatter_labels": ["Mumbai", "New York", "Bangkok", "Jakarta", "São Paulo", "Madrid", "Kuala Lumpur", "Rome", "Athens", "Cape Town"],
                "scatter_colors": ["#3498DB", "#2E86C1", "#85C1E9", "#1B4F72", "#5DADE2", "#21618C", "#AED6F1", "#2980B9", "#A9CCE3", "#154360"],
                "scatter_sizes": [ddd * 20 for ddd in [23, 10, 15, 5, 12, 8, 26, 12, 39, 24]],
                "x_label": "Annual Rainfall (mm)",
                "y_label": "Flood Events/Year",
                "img_title": "Rainfall vs Flood Frequency"
            },
            {
                "scatter_x_data": [5, 12, 3, 18, 25, 8, 14, 20, 4, 22],
                "scatter_y_data": [130, 100, 110, 90, 180, 60, 120, 240, 150, 25],
                "scatter_labels": ["Oslo", "Helsinki", "Reykjavik", "Berlin", "Madrid", "Toronto", "Warsaw", "Paris", "Prague", "Istanbul"],
                "scatter_colors": ["#5DADE2", "#1ABC9C", "#154360", "#E74C3C", "#2980B9", "#BB8FCE", "#58D68D", "#AF601A", "#884EA0", "#F1C40F"],
                "scatter_sizes": [ddd * 8 for ddd in [130, 100, 110, 90, 180, 60, 120, 240, 150, 25]],
                "x_label": "Annual Temp Range (°C)",
                "y_label": "Days Below Freezing",
                "img_title": "Climate Extremes vs Cold Days"
            },
        ],
        "23 - Transportation & Infrastructure": [
            {
                "scatter_x_data": [850, 1400, 600, 1200, 950, 1600, 700, 1350, 1100, 1000],
                "scatter_y_data": [220, 620, 190, 470, 510, 140, 430, 300, 490, 350],
                "scatter_labels": ["California", "Texas", "New Jersey", "Florida", "Illinois", "Ohio", "Georgia", "Pennsylvania", "Arizona", "North Carolina"],
                "scatter_colors": ["#D35400", "#3498DB", "#27AE60", "#F4D03F", "#884EA0", "#1ABC9C", "#F1948A", "#A93226", "#2ECC71", "#7D3C98"],
                "scatter_sizes": [ddd * 1.2 for ddd in [220, 620, 190, 470, 510, 140, 430, 300, 490, 350]],
                "x_label": "State Highway Length (km)",
                "y_label": "Annual Accidents (Thousands)",
                "img_title": "Road Length vs Accidents by State"
            },
            {
                "scatter_x_data": [18, 70, 10, 55, 80, 35, 65, 40, 50, 90],
                "scatter_y_data": [120, 80, 300, 85, 230, 110, 50, 220, 60, 150],
                "scatter_labels": ["Los Angeles", "London", "Beijing", "Tokyo", "Berlin", "Mexico City", "Paris", "Seoul", "New York", "Copenhagen"],
                "scatter_colors": ["#1F618D", "#F1C40F", "#E74C3C", "#58D68D", "#AF7AC5", "#45B39D", "#2E86C1", "#C0392B", "#F4D03F", "#1ABC9C"],
                "scatter_sizes": [ddd * 6 for ddd in [120, 80, 300, 85, 230, 110, 50, 220, 60, 150]],
                "x_label": "Transit Use (% of Population)",
                "y_label": "AQI (Lower is Better)",
                "img_title": "Public Transit vs Urban Air Quality"
            },
        ],
        "24 - Psychology & Personality": [
            {
                "scatter_x_data": [0.5, 1.5, 3, 4, 2.5, 5.5, 6, 2, 7.5, 1],
                "scatter_y_data": [50, 100, 30, 45, 65, 95, 80, 55, 85, 40],
                "scatter_labels": ["Alice", "Brian", "Catherine", "David", "Ella", "Fahim", "Grace", "Henry", "Isabel", "John"],
                "scatter_colors": ["#BB8FCE", "#2980B9", "#1ABC9C", "#E74C3C", "#F1C40F", "#A93226", "#117864", "#D35400", "#2ECC71", "#884EA0"],
                "scatter_sizes": [ddd * 15 for ddd in [50, 100, 30, 45, 65, 95, 80, 55, 85, 40]],
                "x_label": "Social Media Use (Hours/Day)",
                "y_label": "Stress Level (0–100)",
                "img_title": "Digital Habits and Mental Stress"
            },
            {
                "scatter_x_data": [4, 7, 2, 9, 6, 3, 8, 5, 10, 1],
                "scatter_y_data": [60, 88, 72, 97, 85, 78, 55, 50, 95, 45],
                "scatter_labels": ["Alex", "Bella", "Charles", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ian", "Julia"],
                "scatter_colors": ["#58D68D", "#1F618D", "#F5B041", "#6C3483", "#45B39D", "#E74C3C", "#27AE60", "#AF601A", "#5DADE2", "#A93226"],
                "scatter_sizes": [ddd * 16 for ddd in [60, 88, 72, 97, 85, 78, 55, 50, 95, 45]],
                "x_label": "Personality Score (Extraversion)",
                "y_label": "Team Feedback (%)",
                "img_title": "Personality vs Team Approval"
            },
        ],
        "25 - Materials & Engineering": [
            {
                "scatter_x_data": [90, 350, 850, 600, 250, 1200, 700, 180, 500, 1000],
                "scatter_y_data": [30, 8, 15, 25, 10, 18, 20, 35, 22, 12],
                "scatter_labels": ["Copper", "Steel", "Titanium", "Aluminum", "Brass", "Carbon Fiber", "Kevlar", "Nylon", "Bronze", "Inconel"],
                "scatter_colors": ["#884EA0", "#F4D03F", "#5DADE2", "#CA6F1E", "#2ECC71", "#1F618D", "#D98880", "#27AE60", "#A93226", "#AF7AC5"],
                "scatter_sizes": [ddd * 15 for ddd in [30, 8, 15, 25, 10, 18, 20, 35, 22, 12]],
                "x_label": "Tensile Strength (MPa)",
                "y_label": "Ductility (%)",
                "img_title": "Material Strength vs Ductility"
            },
            {
                "scatter_x_data": [401, 385, 237, 150, 120, 70, 25, 0.03, 180, 200],
                "scatter_y_data": [1.7, 2.1, 1.8, 3.0, 3.2, 4.5, 6.0, 20.0, 2.5, 5.9],
                "scatter_labels": ["Copper", "Silver", "Aluminum", "Brass", "Steel", "Titanium", "Glass", "Aerogel", "Zinc", "Graphite"],
                "scatter_colors": ["#F39C12", "#3498DB", "#2ECC71", "#1ABC9C", "#884EA0", "#E74C3C", "#5DADE2", "#F4D03F", "#CA6F1E", "#27AE60"],
                "scatter_sizes": [ddd * 100 for ddd in [1.7, 2.1, 1.8, 3.0, 3.2, 4.5, 6.0, 20.0, 2.5, 5.9]],
                "x_label": "Thermal Conductivity (W/m·K)",
                "y_label": "Electrical Resistivity (µΩ·cm)",
                "img_title": "Thermal vs Electrical Properties of Materials"
            },
        ],
        "26 - Philanthropy & Charity": [
            {
                "scatter_x_data": [500, 1200, 300, 900, 1500, 700, 400, 1100, 800, 600],
                "scatter_y_data": [50_000, 180_000, 200_000, 25_000, 120_000, 350_000, 80_000, 80_000, 100_000, 120_000],
                "scatter_labels": ["Red Cross", "UNICEF", "Oxfam", "Save the Children", "Doctors Without Borders", "CARE", "WaterAid", "WWF", "Amnesty Int'l", "Habitat for Humanity"],
                "scatter_colors": ["#3498DB", "#2E86C1", "#F39C12", "#D35400", "#27AE60", "#229954", "#5DADE2", "#1F618D", "#E74C3C", "#884EA0"],
                "scatter_sizes": [ddd * 0.001 for ddd in [50_000, 180_000, 200_000, 25_000, 120_000, 350_000, 80_000, 80_000, 100_000, 120_000]],
                "x_label": "Annual Donations (Million USD)",
                "y_label": "Beneficiaries Served",
                "img_title": "Charity Funding vs Reach"
            },
            {
                "scatter_x_data": [1200, 2000, 6000, 1800, 1500, 500, 2500, 3000, 800, 1000],
                "scatter_y_data": [75, 60, 82, 70, 55, 80, 90, 68, 72, 85],
                "scatter_labels": ["Red Cross", "UNICEF", "Oxfam", "Habitat for Humanity", "Doctors Without Borders", "CARE", "WWF", "Amnesty Int'l", "WaterAid", "Save the Children"],
                "scatter_colors": ["#F1C40F", "#B7950B", "#2ECC71", "#1E8449", "#2980B9", "#21618C", "#E74C3C", "#943126", "#BB8FCE", "#6C3483"],
                "scatter_sizes": [ddd * 3 for ddd in [75, 60, 82, 70, 55, 80, 90, 68, 72, 85]],
                "x_label": "Volunteer Hours (Thousands)",
                "y_label": "Impact Score (0-100)",
                "img_title": "Volunteer Engagement vs Effectiveness"
            },
        ],
        "27 - Fashion & Apparel": [
            {
                "scatter_x_data": [250, 200, 450, 120, 600, 150, 180, 400, 320, 550],
                "scatter_y_data": [15_000, 22_000, 8_000, 30_000, 5_500, 12_000, 25_000, 9_000, 28_000, 6_500],
                "scatter_labels": ["Gucci Bag", "Prada Shoes", "Louis Vuitton", "Zara Coat", "Chanel Dress", "Burberry Scarf", "H&M Dress", "Versace Sunglasses", "Uniqlo Jacket", "Dior Perfume"],
                "scatter_colors": ["#A93226", "#C0392B", "#884EA0", "#2ECC71", "#F39C12", "#F1C40F", "#27AE60", "#9B59B6", "#5DADE2", "#E74C3C"],
                "scatter_sizes": [ddd * 0.03 for ddd in [15_000, 22_000, 8_000, 30_000, 5_500, 12_000, 25_000, 9_000, 28_000, 6_500]],
                "x_label": "Price ($)",
                "y_label": "Monthly Sales Volume",
                "img_title": "Luxury Item Price vs Sales"
            },
            {
                "scatter_x_data": [5_000, 12_000, 3_500, 15_000, 9_500, 10_000, 9_000, 7_000, 8_500, 6_000],
                "scatter_y_data": [1, 4, 2, 5, 3, 6, 4, 2, 5, 3],
                "scatter_labels": ["Black", "Pastel Pink", "Neon Green", "Royal Blue", "Beige", "Maroon", "Teal", "Orange", "Lavender", "Mustard"],
                "scatter_colors": ["#000000", "#FFC0CB", "#39FF14", "#4169E1", "#F5F5DC", "#800000", "#008080", "#FFA500", "#E6E6FA", "#FFDB58"],
                "scatter_sizes": [ddd * 0.1 for ddd in [5_000, 12_000, 3_500, 15_000, 9_500, 10_000, 9_000, 7_000, 8_500, 6_000]],
                "x_label": "Instagram Mentions",
                "y_label": "Season (1=Winter…6=Autumn)",
                "img_title": "Color Trends Across Seasons"
            },
        ],
        "28 - Parenting & Child Development": [
            {
                "scatter_x_data": [1, 5, 3.5, 0.5, 3, 1.5, 2, 4, 2.5, 4.5],
                "scatter_y_data": [11, 9, 10, 8, 7, 12, 9.5, 10.5, 11.5, 8.5],
                "scatter_labels": ["Age 2-3","Age 10-11","Age 3-4","Age 7-8","Age 9-10","Age 1-2","Age 6-7","Age 5-6","Age 4-5","Age 8-9"],
                "scatter_colors": ["#58D68D","#1F618D","#A93226","#F39C12","#27AE60","#884EA0","#5DADE2","#D35400","#BB8FCE","#E74C3C"],
                "scatter_sizes": [ddd * 30 for ddd in [11, 9, 10, 8, 7, 12, 9.5, 10.5, 11.5, 8.5]],
                "x_label": "Daily Screen Time (Hours)",
                "y_label": "Nightly Sleep (Hours)",
                "img_title": "Kids' Screen Time vs Sleep"
            },
            {
                "scatter_x_data": [0.5, 1, 2, 3, 0.8, 1.5, 2.5, 3.5, 0.2, 4],
                "scatter_y_data": [200, 500, 800, 1200, 1800, 2300, 3100, 3800, 4500, 6000],
                "scatter_labels": ["Age 1","Age 2","Age 3","Age 4","Age 5","Age 6","Age 7","Age 8","Age 9","Age 10"],
                "scatter_colors": ["#2ECC71","#117A65","#3498DB","#9B59B6","#F1C40F","#883E23","#5DADE2","#AF601A","#D98880","#A93226"],
                "scatter_sizes": [ddd * 0.1 for ddd in [200, 500, 800, 1200, 1800, 2300, 3100, 3800, 4500, 6000]],
                "x_label": "Daily Reading Time (Hours)",
                "y_label": "Vocabulary Size (Words)",
                "img_title": "Early Reading vs Vocabulary Growth"
            },
        ],
        "29 - Architecture & Urban Planning": [
            {
                "scatter_x_data": [5, 2, 12, 10, 15, 4, 14, 6, 3, 8],
                "scatter_y_data": [8300, 3200, 15000, 4500, 2100, 18000, 2700, 7200, 11000, 2300],
                "scatter_labels": ["New York","London","Tokyo","Paris","Sydney","Mumbai","Berlin","Toronto","Beijing","Melbourne"],
                "scatter_colors": ["#27AE60","#145A32","#3498DB","#1F618D","#82E0AA","#196F3D","#5DADE2","#21618C","#A93226","#239B56"],
                "scatter_sizes": [ddd * 0.1 for ddd in [8300, 3200, 15000, 4500, 2100, 18000, 2700, 7200, 11000, 2300]],
                "x_label": "Green Space per Capita (m²)",
                "y_label": "Population Density (per km²)",
                "img_title": "Urban Greenery vs Density"
            },
            {
                "scatter_x_data": [50, 200, 70, 120, 250, 90, 180, 40, 150, 30],
                "scatter_y_data": [0.9, 0.6, 1.2, 0.8, 0.5, 1.0, 1.1, 0.7, 0.95, 0.65],
                "scatter_labels": ["Empire State","Burj Khalifa","Flatiron","Willis Tower","Shanghai Tower","The Shard","Gherkin","Taipei 101","One World Trade","Petronas Towers"],
                "scatter_colors": ["#F39C12","#D35400","#3498DB","#2980B9","#884EA0","#5DADE2","#1ABC9C","#1F618D","#E74C3C","#A93226"],
                "scatter_sizes": [ddd * 1000 for ddd in [0.9, 0.6, 1.2, 0.8, 0.5, 1.0, 1.1, 0.7, 0.95, 0.65]],
                "x_label": "Building Height (m)",
                "y_label": "Energy Efficiency (kWh/m²·year)",
                "img_title": "Skyscraper Height vs Efficiency"
            },
        ],
        "30 - Gaming & Recreation": [
            {
                "scatter_x_data": [30, 45, 60, 50, 40, 55, 70, 25, 20, 65],
                "scatter_y_data": [8.5, 9.0, 7.8, 9.5, 8.8, 9.7, 8.0, 8.6, 9.2, 9.4],
                "scatter_labels": ["The Witcher 3","Skyrim","Among Us","Elden Ring","Minecraft","Cyberpunk 2077","Stardew Valley","Celeste","God of War","Hades"],
                "scatter_colors": ["#27AE60","#145A32","#E74C3C","#884EA0","#3498DB","#A93226","#5DADE2","#F1C40F","#1F618D","#D35400"],
                "scatter_sizes": [ddd * 100 for ddd in [8.5, 9.0, 7.8, 9.5, 8.8, 9.7, 8.0, 8.6, 9.2, 9.4]],
                "x_label": "Avg. Play Time (Hours)",
                "y_label": "User Rating (0-10)",
                "img_title": "Playtime vs Popularity in Games"
            },
            {
                "scatter_x_data": [5, 20, 3, 15, 8, 18, 12, 7, 10, 25],
                "scatter_y_data": [0.5, 1.2, 0.3, 2.5, 0.8, 3.0, 1.5, 1.7, 2.0, 3.5],
                "scatter_labels": ["Candy Crush","Clash of Clans","Among Us","Pokémon Go","Angry Birds","PUBG Mobile","Genshin Impact","Temple Run","Roblox","Fortnite"],
                "scatter_colors": ["#F39C12","#D35400","#E74C3C","#27AE60","#229954","#884EA0","#5DADE2","#1F618D","#A93226","#2980B9"],
                "scatter_sizes": [ddd * 100 for ddd in [0.5, 1.2, 0.3, 2.5, 0.8, 3.0, 1.5, 0.7, 2.0, 3.5]],
                "x_label": "Downloads (Millions)",
                "y_label": "Paid Users (%)",
                "img_title": "Mobile Game Popularity vs Monetization"
            },
        ], 
    }
}



METADATA_LINE = {
    "draw__4_line__func_1": {
        "1 - Media & Entertainment": [
            {
                "line_data": [
                    [25.5, 32.2, 35.8, 42.1, 33.9, 46.3],
                    [18.3, 22.7, 28.4, 33.6, 39.2, 42.8],
                    [31.2, 28.9, 32.5, 36.7, 41.3, 38.9],
                    [12.8, 15.4, 19.6, 24.3, 29.1, 33.7],
                ],
                "line_labels": ["Netflix", "Comcast", "Walt Disney", "Charter Communications"],
                "line_category": {"singular": "media company", "plural": "media companies"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Revenue ($ Million)",
                "img_title": "Media Company Revenue Trends (2019-2024)",
            },
            {
                "line_data": [
                    [14.7, 16.8, 19.4, 23.1, 25.9, 29.5],
                    [8.2, 9.5, 11.7, 13.4, 15.6, 18.2],
                    [20.5, 22.9, 25.6, 28.3, 30.8, 34.1],
                    [5.4, 6.3, 7.1, 8.7, 9.5, 10.8],
                ],
                "line_labels": ["Paramount Global", "Sony Pictures", "Warner Bros. Discovery", "Lionsgate"],
                "line_category": {"singular": "studio", "plural": "studios"},
                "line_colors": ["#9B59B6", "#1ABC9C", "#E67E22", "#F4495E"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Box Office Revenue ($ Billion)",
                "img_title": "Major Studios Box Office Revenue Trends (2019-2024)",
            },
        ],
        "2 - Geography & Demography": [
            {
                "line_data": [
                    [37.1, 30.1, 30.8, 40.7, 41.5, 42.3],
                    [34.6, 35.4, 36.2, 28.6, 29.1, 38.0],
                    [29.3, 38.2, 39.4, 31.4, 32.0, 32.5],
                    [27.0, 27.5, 28.0, 29.6, 36.9, 35.5],
                ],
                "line_labels": ["Tokyo", "New York", "London", "Paris"],
                "line_category": {"singular": "city", "plural": "cities"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Population (Million)",
                "img_title": "Urban Population Growth Trends (2019-2024)",
            },
            {
                "line_data": [
                    [38.5, 49.0, 39.3, 39.7, 40.0, 50.4],
                    [35.2, 63.5, 44.8, 54.1, 68.3, 72.6],
                    [32.1, 76.5, 76.8, 83.0, 77.3, 87.6],
                    [46.5, 66.9, 57.2, 63.5, 62.8, 47.1],
                ],
                "line_labels": ["Japan", "Switzerland", "United States", "Brazil"],
                "line_category": {"singular": "country", "plural": "countries"},
                "line_colors": ["#9B59B6", "#1ABC9C", "#E67E22", "#F62459"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Average Life Expectancy (Years)",
                "img_title": "Life Expectancy in Selected Countries (2019-2024)",
            },
        ],
        "3 - Education & Academia": [
            {
                "line_data": [
                    [5.2, 5.5, 5.7, 6.0, 6.3, 6.5],
                    [4.0, 4.2, 4.5, 4.7, 4.9, 5.2],
                    [6.8, 7.1, 7.3, 7.5, 7.8, 8.0],
                    [3.5, 3.7, 3.8, 4.0, 4.2, 4.4],
                ],
                "line_labels": ["Harvard", "Stanford", "MIT", "Yale"],
                "line_category": {"singular": "university", "plural": "universities"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Research Funding ($ Billion)",
                "img_title": "Research Funding of Top US Universities (2019-2024)",
            },
            {
                "line_data": [
                    [15000, 12200, 12500, 15800, 16000, 16300],
                    [12000, 18250, 18500, 12750, 13000, 13300],
                    [18000, 15200, 15500, 18800, 19000, 19300],
                    [14000, 14250, 14500, 14750, 15000, 15250],
                ],
                "line_labels": ["University of Oxford", "University of Cambridge", "University of Tokyo", "University of Melbourne"],
                "line_category": {"singular": "university", "plural": "universities"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "International Student Enrollment",
                "img_title": "Growth in International Student Numbers (2019-2024)",
            }
        ],
        "4 - Business & Industry": [
            {
                "line_data": [
                    [260, 275, 290, 310, 330, 355],
                    [190, 210, 230, 250, 270, 295],
                    [300, 320, 340, 365, 390, 420],
                    [150, 165, 180, 195, 210, 230],
                ],
                "line_labels": ["Apple", "Microsoft", "Amazon", "Alphabet"],
                "line_category": {"singular": "company", "plural": "companies"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Market Cap ($ Billion)",
                "img_title": "Market Capitalization Trends of Big Tech (2019-2024)",
            },
            {
                "line_data": [
                    [55, 60, 65, 68, 72, 75],
                    [42, 46, 50, 60, 64, 68],
                    [48, 52, 57, 53, 57, 60],
                    [35, 38, 42, 45, 48, 51],
                ],
                "line_labels": ["Tesla", "Volkswagen", "Toyota", "Ford"],
                "line_category": {"singular": "automaker", "plural": "automakers"},
                "line_colors": ["#9B59B6", "#1ABC9C", "#E67E22", "#F62459"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Vehicle Production (Million Units)",
                "img_title": "Global Vehicle Production by Automakers (2019-2024)",
            },
        ],
        "5 - Major & Course": [
            {
                "line_data": [
                    [14000, 14500, 19000, 23500, 24000, 24500],
                    [22000, 22500, 23000, 19500, 20000, 20500],
                    [10000, 10500, 15000, 15500, 16000, 16500],
                    [18000, 18500, 11000, 11500, 12000, 12500],
                ],
                "line_labels": ["Computer Science", "Business Administration", "Biology", "Psychology"],
                "line_category": {"singular": "major", "plural": "majors"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Enrollment (Number of Students)",
                "img_title": "Enrollment Trends of Popular Majors (2019-2024)",
            },
            {
                "line_data": [
                    [88, 90, 92, 94, 96, 97],
                    [76, 78, 80, 82, 84, 86],
                    [82, 83, 85, 75, 77, 78],
                    [69, 71, 73, 88, 89, 90],
                ],
                "line_labels": ["Data Science", "Finance", "Mechanical Engineering", "Sociology"],
                "line_category": {"singular": "course", "plural": "courses"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Average Course Satisfaction (%)",
                "img_title": "Course Satisfaction Scores Over Time (2019-2024)",
            },
        ],
        "6 - Animal & Zoology": [
            {
                "line_data": [
                    [415, 420, 425, 430, 435, 440],
                    [250, 255, 260, 265, 270, 275],
                    [80, 82, 85, 88, 90, 93],
                    [30, 32, 34, 36, 38, 40],
                ],
                "line_labels": ["African Elephant", "Tiger", "Gorilla", "Panda"],
                "line_category": {"singular": "species", "plural": "species"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Population in Reserves (Thousands)",
                "img_title": "Endangered Species Population in Reserves (2019-2024)",
            },
            {
                "line_data": [
                    [180, 185, 190, 200, 210, 220],
                    [120, 125, 130, 135, 140, 145],
                    [300, 310, 320, 330, 340, 350],
                    [50, 55, 60, 65, 70, 75],
                ],
                "line_labels": ["Bald Eagle", "Snow Leopard", "Blue Whale", "Red Panda"],
                "line_category": {"singular": "animal", "plural": "animals"},
                "line_colors": ["#9B59B6", "#1ABC9C", "#E67E22", "#F62459"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Estimated Global Population",
                "img_title": "Population Trends of Iconic Animals (2019-2024)",
            },
        ],
        "7 - Plant & Botany": [
            {
                "line_data": [
                    [55, 59, 62, 77, 80, 83],
                    [25, 27, 29, 41, 44, 47],
                    [70, 72, 74, 53, 56, 68],
                    [45, 48, 52, 31, 33, 35],
                ],
                "line_labels": ["Oak", "Maple", "Pine", "Birch"],
                "line_category": {"singular": "tree species", "plural": "tree species"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Forest Coverage (Million Acres)",
                "img_title": "Forest Coverage by Tree Species (2019-2024)",
            },
            {
                "line_data": [
                    [20, 22, 24, 27, 30, 33],
                    [15, 17, 19, 13, 15, 18],
                    [12, 14, 16, 22, 24, 27],
                    [8, 10, 12, 18, 20, 23],
                ],
                "line_labels": ["Sunflower", "Rose", "Tulip", "Lavender"],
                "line_category": {"singular": "flower species", "plural": "flower species"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Cultivation Area (Thousand Hectares)",
                "img_title": "Flower Cultivation Trends (2019-2024)",
            },
        ],
        "8 - Biology & Chemistry": [
            {
                "line_data": [
                    [3.2, 3.5, 3.9, 5.4, 5.7, 6.0],
                    [2.0, 2.3, 2.6, 2.9, 3.2, 3.5],
                    [4.5, 4.8, 5.1, 4.3, 4.7, 5.0],
                    [1.2, 1.5, 1.7, 1.9, 2.2, 2.4],
                ],
                "line_labels": ["CRISPR Gene Editing", "Synthetic Biology", "mRNA Technology", "Stem Cell Therapy"],
                "line_category": {"singular": "research field", "plural": "research fields"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Global Funding ($ Billion)",
                "img_title": "Funding Growth in Biotech Fields (2019-2024)",
            },
            {
                "line_data": [
                    [45, 47, 50, 52, 55, 58],
                    [30, 28, 30, 15, 17, 18],
                    [20, 22, 24, 37, 39, 42],
                    [10, 12, 14, 26, 28, 31],
                ],
                "line_labels": ["Organic Chemistry", "Inorganic Chemistry", "Analytical Chemistry", "Physical Chemistry"],
                "line_category": {"singular": "chemistry field", "plural": "chemistry fields"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Number of Publications (Thousands)",
                "img_title": "Publication Trends in Chemistry (2019-2024)",
            },
        ],
        "9 - Food & Nutrition": [
            {
                "line_data": [
                    [150, 160, 170, 185, 195, 205],
                    [120, 125, 130, 138, 145, 152],
                    [90, 95, 100, 108, 115, 122],
                    [60, 65, 70, 76, 82, 88],
                ],
                "line_labels": ["Organic Vegetables", "Whole Grains", "Plant-Based Meat", "Fermented Foods"],
                "line_category": {"singular": "food category", "plural": "food categories"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Global Sales ($ Million)",
                "img_title": "Growth of Health Food Categories (2019-2024)",
            },
            {
                "line_data": [
                    [45, 48, 52, 56, 61, 66],
                    [30, 32, 35, 15, 17, 18],
                    [25, 27, 29, 38, 42, 46],
                    [38, 42, 44, 22, 26, 32],
                ],
                "line_labels": ["Vitamin Supplements", "Protein Powders", "Omega-3 Products", "Probiotics"],
                "line_category": {"singular": "supplement", "plural": "supplements"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Market Size ($ Billion)",
                "img_title": "Supplement Market Expansion (2019-2024)",
            },
        ],
        "10 - Space & Astronomy": [
            {
                "line_data": [
                    [15, 17, 20, 17, 20, 23],
                    [10, 12, 15, 23, 26, 30],
                    [5, 7, 9, 11, 14, 17],
                    [3, 4, 5, 6, 8, 10],
                ],
                "line_labels": ["NASA", "SpaceX", "ESA", "JAXA"],
                "line_category": {"singular": "space agency", "plural": "space agencies"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Annual Launches",
                "img_title": "Annual Space Launches by Agency (2019-2024)",
            },
            {
                "line_data": [
                    [450, 460, 470, 330, 340, 350],
                    [380, 390, 400, 480, 490, 500],
                    [300, 310, 320, 410, 420, 430],
                    [250, 260, 270, 280, 290, 300],
                ],
                "line_labels": ["Hubble", "James Webb", "Chandra", "Spitzer"],
                "line_category": {"singular": "telescope", "plural": "telescopes"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Published Observations (Count)",
                "img_title": "Scientific Observations from Space Telescopes (2019-2024)",
            },
        ],
        "11 - Sale & Merchandise": [
            {
                "line_data": [
                    [200, 220, 240, 265, 290, 320],
                    [150, 165, 180, 135, 150, 165],
                    [180, 195, 210, 225, 245, 270],
                    [100, 110, 120, 195, 210, 230],
                ],
                "line_labels": ["Amazon", "eBay", "Walmart", "Target"],
                "line_category": {"singular": "retailer", "plural": "retailers"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Online Sales ($ Billion)",
                "img_title": "E-commerce Sales Growth (2019-2024)",
            },
            {
                "line_data": [
                    [50, 55, 60, 68, 75, 83],
                    [35, 38, 42, 46, 51, 57],
                    [28, 32, 36, 25, 28, 31],
                    [18, 20, 23, 39, 43, 47],
                ],
                "line_labels": ["Nike", "Adidas", "Lululemon", "Under Armour"],
                "line_category": {"singular": "brand", "plural": "brands"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Apparel Revenue ($ Billion)",
                "img_title": "Global Sportswear Brand Revenue (2019-2024)",
            },
        ],
        "12 - Market & Economy": [
            {
                "line_data": [
                    [2.1, 2.3, 2.5, 2.7, 3.0, 3.3],
                    [1.5, 1.7, 1.9, 1.5, 1.6, 1.8],
                    [3.0, 3.2, 3.5, 3.8, 4.1, 4.5],
                    [1.0, 1.2, 1.3, 2.1, 2.3, 2.5],
                ],
                "line_labels": ["United States", "Germany", "China", "India"],
                "line_category": {"singular": "economy", "plural": "economies"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "GDP Growth (%)",
                "img_title": "GDP Growth Rates by Country (2019-2024)",
            },
            {
                "line_data": [
                    [15, 17, 20, 23, 26, 30],
                    [10, 12, 15, 13, 15, 18],
                    [8, 9, 11, 17, 19, 22],
                    [5, 6, 7, 8, 9, 11],
                ],
                "line_labels": ["S&P 500", "NASDAQ", "FTSE 100", "Nikkei 225"],
                "line_category": {"singular": "index", "plural": "indices"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Index Growth (%)",
                "img_title": "Major Stock Index Performance (2019-2024)",
            },
        ],
        "13 - Sports & Athletics": [
            {
                "line_data": [
                    [80, 85, 90, 96, 102, 108],
                    [65, 70, 75, 68, 73, 78],
                    [55, 60, 64, 80, 85, 90],
                    [45, 48, 52, 56, 60, 65],
                ],
                "line_labels": ["Premier League", "La Liga", "Bundesliga", "Serie A"],
                "line_category": {"singular": "league", "plural": "leagues"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Revenue ($ Billion)",
                "img_title": "European Football League Revenue (2019-2024)",
            },
            {
                "line_data": [
                    [22, 24, 26, 29, 31, 34],
                    [18, 19, 21, 27, 22, 28],
                    [14, 15, 16, 15, 16, 17],
                    [12, 13, 14, 18, 20, 22],
                ],
                "line_labels": ["NBA", "NFL", "MLB", "NHL"],
                "line_category": {"singular": "league", "plural": "leagues"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Viewership (Million Average)",
                "img_title": "US Major League Viewership Trends (2019-2024)",
            },
        ],
        "14 - Computing & Technology": [
            {
                "line_data": [
                    [25, 28, 32, 34, 24, 21],
                    [30, 35, 40, 46, 52, 60],
                    [20, 22, 25, 39, 40, 44],
                    [15, 17, 19, 28, 32, 36],
                ],
                "line_labels": ["Cloud Computing", "AI & ML", "Cybersecurity", "IoT"],
                "line_category": {"singular": "technology sector", "plural": "technology sectors"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Market Value ($ Billion)",
                "img_title": "Technology Sector Growth Trends (2019-2024)",
            },
            {
                "line_data": [
                    [45, 48, 52, 46, 50, 55],
                    [35, 38, 34, 37, 40, 44],
                    [28, 31, 42, 56, 61, 66],
                    [20, 22, 25, 28, 30, 33],
                ],
                "line_labels": ["Apple", "Samsung", "Huawei", "Xiaomi"],
                "line_category": {"singular": "smartphone brand", "plural": "smartphone brands"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Smartphone Shipments (Million Units)",
                "img_title": "Global Smartphone Shipments (2019-2024)",
            },
        ],
        "15 - Health & Medicine": [
            {
                "line_data": [
                    [120, 125, 130, 138, 145, 152],
                    [80, 85, 90, 96, 102, 110],
                    [60, 64, 68, 50, 54, 58],
                    [40, 43, 46, 73, 78, 84],
                ],
                "line_labels": ["Pfizer", "Johnson & Johnson", "Roche", "Merck"],
                "line_category": {"singular": "pharmaceutical company", "plural": "pharmaceutical companies"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Revenue ($ Billion)",
                "img_title": "Top Pharmaceutical Companies Revenue (2019-2024)",
            },
            {
                "line_data": [
                    [60, 63, 67, 71, 75, 80],
                    [45, 38, 45, 37, 40, 42],
                    [35, 48, 51, 54, 58, 62],
                    [25, 27, 29, 31, 33, 36],
                ],
                "line_labels": ["Cardiology", "Oncology", "Neurology", "Orthopedics"],
                "line_category": {"singular": "medical specialty", "plural": "medical specialties"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Annual Research Funding ($ Billion)",
                "img_title": "Funding Trends by Medical Specialty (2019-2024)",
            },
        ],
        "16 - Energy & Environment": [
            {
                "line_data": [
                    [500, 520, 540, 560, 580, 600],
                    [450, 470, 490, 510, 530, 550],
                    [300, 320, 340, 360, 380, 400],
                    [200, 215, 230, 245, 260, 275],
                ],
                "line_labels": ["Solar", "Wind", "Hydropower", "Geothermal"],
                "line_category": {"singular": "energy source", "plural": "energy sources"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Installed Capacity (GW)",
                "img_title": "Renewable Energy Capacity Growth (2019-2024)",
            },
            {
                "line_data": [
                    [15, 17, 18, 20, 22, 25],
                    [10, 11, 12, 11, 12, 13],
                    [8, 9, 10, 13, 14, 15],
                    [5, 6, 7, 8, 9, 10],
                ],
                "line_labels": ["CO2 Emissions", "Methane Emissions", "Nitrous Oxide", "Fluorinated Gases"],
                "line_category": {"singular": "emission type", "plural": "emission types"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Annual Emissions (Billion Tons CO2 eq.)",
                "img_title": "Global Greenhouse Gas Emissions (2019-2024)",
            },
        ],
        "17 - Travel & Expedition": [
            {
                "line_data": [
                    [180, 195, 210, 230, 250, 270],
                    [120, 135, 150, 165, 180, 195],
                    [90, 100, 110, 95, 88, 72],
                    [60, 70, 80, 120, 130, 140],
                ],
                "line_labels": ["Delta", "Emirates", "Lufthansa", "Singapore Airlines"],
                "line_category": {"singular": "airline", "plural": "airlines"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Passenger Volume (Million)",
                "img_title": "Major Airlines Passenger Traffic (2019-2024)",
            },
            {
                "line_data": [
                    [2.5, 2.7, 3.0, 2.5, 2.7, 3.0],
                    [1.8, 2.0, 2.3, 3.3, 3.7, 4.0],
                    [1.2, 1.0, 1.2, 1.4, 1.5, 1.7],
                    [0.9, 1.4, 1.6, 1.8, 2.0, 2.3],
                ],
                "line_labels": ["Mount Everest", "Kilimanjaro", "Denali", "Matterhorn"],
                "line_category": {"singular": "expedition site", "plural": "expedition sites"},
                "line_colors": ["#9B59B6", "#E67E22", "#2ECC71", "#71A7DA"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Annual Climbers (Thousands)",
                "img_title": "Mountain Expeditions Popularity (2019-2024)",
            },
        ],
        "18 - Arts & Culture": [
            {
                "line_data": [
                    [8.0, 8.5, 9.0, 9.6, 10.3, 11.0],
                    [5.5, 5.8, 4.6, 4.9, 5.2, 5.5],
                    [4.0, 4.3, 6.2, 6.5, 6.9, 7.3],
                    [2.5, 2.7, 3.0, 3.2, 2.9, 2.7],
                ],
                "line_labels": ["MoMA", "Louvre", "Tate Modern", "Uffizi"],
                "line_category": {"singular": "museum", "plural": "museums"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Annual Visitors (Million)",
                "img_title": "Museum Visitor Trends (2019-2024)",
            },
            {
                "line_data": [
                    [500, 520, 540, 560, 580, 600],
                    [350, 370, 390, 410, 430, 450],
                    [250, 260, 220, 230, 200, 210],
                    [180, 190, 270, 280, 290, 300],
                ],
                "line_labels": ["Art Basel", "Frieze", "Venice Biennale", "Documenta"],
                "line_category": {"singular": "art fair", "plural": "art fairs"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Artworks Sold",
                "img_title": "Art Fair Sales Performance (2019-2024)",
            },
        ],
        "19 - Communication & Collaboration": [
            {
                "line_data": [
                    [50, 55, 60, 67, 75, 83],
                    [40, 44, 40, 48, 38, 33],
                    [30, 35, 50, 55, 61, 68],
                    [20, 26, 36, 40, 44, 48],
                ],
                "line_labels": ["Zoom", "Microsoft Teams", "Slack", "Google Meet"],
                "line_category": {"singular": "platform", "plural": "platforms"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Monthly Active Users (Million)",
                "img_title": "Growth of Collaboration Platforms (2019-2024)",
            },
            {
                "line_data": [
                    [900, 770, 640, 660, 680, 700],
                    [750, 920, 940, 960, 980, 1000],
                    [600, 620, 790, 810, 830, 850],
                    [450, 470, 490, 510, 530, 550],
                ],
                "line_labels": ["WhatsApp", "WeChat", "Messenger", "Telegram"],
                "line_category": {"singular": "messaging app", "plural": "messaging apps"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Global Users (Million)",
                "img_title": "Messaging App User Growth (2019-2024)",
            },
        ],
        "20 - Language & Linguistics": [
            {
                "line_data": [
                    [1.2, 1.3, 1.4, 1.5, 1.6, 1.7],
                    [0.8, 0.9, 1.0, 1.1, 1.2, 1.3],
                    [0.6, 0.65, 0.7, 0.65, 0.6, 0.45],
                    [0.4, 0.45, 0.5, 0.75, 0.8, 0.85],
                ],
                "line_labels": ["English", "Mandarin", "Spanish", "Hindi"],
                "line_category": {"singular": "language", "plural": "languages"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Learners Worldwide (Billion)",
                "img_title": "Global Language Learning Trends (2019-2024)",
            },
            {
                "line_data": [
                    [100, 110, 120, 130, 140, 150],
                    [70, 75, 80, 85, 90, 95],
                    [50, 54, 58, 39, 42, 45],
                    [30, 33, 36, 60, 66, 62],
                ],
                "line_labels": ["Grammarly", "Duolingo", "Babbel", "Busuu"],
                "line_category": {"singular": "language app", "plural": "language apps"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Active Users (Million)",
                "img_title": "User Growth of Language Apps (2019-2024)",
            },
        ],
        "21 - History & Archaeology": [
            {
                "line_data": [
                    [50, 55, 60, 65, 70, 75],
                    [40, 42, 45, 48, 52, 56],
                    [30, 33, 36, 39, 42, 45],
                    [20, 22, 24, 26, 28, 30],
                ],
                "line_labels": ["Egypt", "Greece", "Rome", "Mesoamerica"],
                "line_category": {"singular": "ancient civilization", "plural": "ancient civilizations"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Excavations Conducted",
                "img_title": "Archaeological Excavations by Region (2019-2024)",
            },
            {
                "line_data": [
                    [120, 125, 130, 136, 142, 148],
                    [90, 93, 96, 107, 99, 103],
                    [70, 73, 76, 56, 58, 60],
                    [50, 52, 54, 79, 82, 85],
                ],
                "line_labels": ["Smithsonian", "British Museum", "Louvre", "Metropolitan Museum"],
                "line_category": {"singular": "museum", "plural": "museums"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Artifacts Acquired",
                "img_title": "Artifact Acquisition by Museums (2019-2024)",
            },
        ],
        "22 - Weather & Climate": [
            {
                "line_data": [
                    [14.8, 14.9, 15.1, 15.3, 15.5, 15.7],
                    [12.3, 12.4, 12.5, 12.7, 12.9, 13.0],
                    [9.5, 9.6, 9.8, 9.9, 10.1, 10.2],
                    [7.0, 7.1, 7.2, 7.4, 7.5, 7.7],
                ],
                "line_labels": ["Global Avg", "Northern Hemisphere", "Southern Hemisphere", "Arctic"],
                "line_category": {"singular": "region", "plural": "regions"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Average Temperature (°C)",
                "img_title": "Regional Temperature Changes (2019-2024)",
            },
            {
                "line_data": [
                    [20, 22, 25, 28, 31, 34],
                    [15, 17, 12, 18, 15, 16],
                    [10, 11, 19, 21, 23, 26],
                    [5, 6, 7, 8, 12, 10],
                ],
                "line_labels": ["Atlantic", "Pacific", "Indian Ocean", "Mediterranean"],
                "line_category": {"singular": "ocean basin", "plural": "ocean basins"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Storm Events Recorded",
                "img_title": "Major Storm Events by Ocean Basin (2019-2024)",
            },
        ],
        "23 - Transportation & Infrastructure": [
            {
                "line_data": [
                    [320, 340, 360, 380, 360, 480],
                    [280, 300, 320, 340, 430, 520],
                    [200, 220, 170, 180, 190, 200],
                    [150, 160, 240, 260, 280, 300],
                ],
                "line_labels": ["Japan", "China", "France", "Germany"],
                "line_category": {"singular": "country", "plural": "countries"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "High-Speed Rail Passengers (Million)",
                "img_title": "High-Speed Rail Ridership by Country (2019-2024)",
            },
            {
                "line_data": [
                    [50, 52, 54, 34, 36, 38],
                    [35, 37, 39, 42, 45, 48],
                    [28, 30, 32, 57, 60, 63],
                    [18, 19, 21, 23, 25, 27],
                ],
                "line_labels": ["Maersk", "MSC", "COSCO", "CMA CGM"],
                "line_category": {"singular": "shipping company", "plural": "shipping companies"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Container Volume (Million TEU)",
                "img_title": "Container Shipping Volumes (2019-2024)",
            },
        ],
        "24 - Psychology & Personality": [
            {
                "line_data": [
                    [30, 32, 35, 38, 41, 45],
                    [20, 22, 24, 26, 28, 30],
                    [15, 16, 18, 15, 13, 10],
                    [10, 11, 12, 20, 21, 23],
                ],
                "line_labels": ["Mindfulness", "Cognitive Therapy", "Behavioral Therapy", "Psychoanalysis"],
                "line_category": {"singular": "therapy type", "plural": "therapy types"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Therapy Sessions (Million)",
                "img_title": "Popularity of Therapy Types (2019-2024)",
            },
            {
                "line_data": [
                    [60, 62, 44, 47, 49, 52],
                    [40, 42, 65, 68, 72, 75],
                    [25, 27, 29, 31, 33, 35],
                    [15, 16, 17, 18, 12, 8],
                ],
                "line_labels": ["Introversion", "Extroversion", "Ambiversion", "Highly Sensitive"],
                "line_category": {"singular": "personality trait", "plural": "personality traits"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Population (%)",
                "img_title": "Distribution of Personality Traits (2019-2024)",
            },
        ],
        "25 - Materials & Engineering": [
            {
                "line_data": [
                    [100, 105, 110, 116, 122, 128],
                    [80, 85, 90, 71, 75, 108],
                    [60, 63, 67, 95, 100, 98],
                    [40, 42, 45, 48, 52, 56],
                ],
                "line_labels": ["Steel", "Aluminum", "Concrete", "Carbon Fiber"],
                "line_category": {"singular": "material", "plural": "materials"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Global Demand (Million Tons)",
                "img_title": "Global Material Demand Trends (2019-2024)",
            },
            {
                "line_data": [
                    [15, 17, 19, 21, 23, 25],
                    [10, 11, 12, 13, 14, 15],
                    [6, 5, 6, 3, 2, 7],
                    [3, 7, 8, 9, 10, 11],
                ],
                "line_labels": ["Semiconductors", "Nanomaterials", "Bioplastics", "Graphene"],
                "line_category": {"singular": "advanced material", "plural": "advanced materials"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Research Publications (Thousands)",
                "img_title": "Research Focus on Advanced Materials (2019-2024)",
            },
        ],
        "26 - Philanthropy & Charity": [
            {
                "line_data": [
                    [8, 9, 10, 8.5, 9.6, 10.8],
                    [5, 6, 7, 11, 12, 13],
                    [4, 4.5, 5, 5.5, 6, 6.5],
                    [3, 3.2, 3.5, 3.8, 4, 4.3],
                ],
                "line_labels": ["Gates Foundation", "Open Society", "Ford Foundation", "Wellcome Trust"],
                "line_category": {"singular": "foundation", "plural": "foundations"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Annual Giving ($ Billion)",
                "img_title": "Major Foundation Donations (2019-2024)",
            },
            {
                "line_data": [
                    [100, 110, 120, 135, 150, 165],
                    [70, 80, 60, 65, 70, 75],
                    [50, 55, 90, 100, 110, 120],
                    [30, 32, 34, 36, 38, 40],
                ],
                "line_labels": ["Red Cross", "UNICEF", "Oxfam", "Doctors Without Borders"],
                "line_category": {"singular": "organization", "plural": "organizations"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Donations Received ($ Million)",
                "img_title": "Annual Donations to NGOs (2019-2024)",
            },
        ],
        "27 - Fashion & Apparel": [
            {
                "line_data": [
                    [35, 38, 42, 46, 50, 54],
                    [25, 27, 30, 26, 28, 30],
                    [20, 22, 24, 33, 36, 39],
                    [15, 16, 18, 20, 22, 24],
                ],
                "line_labels": ["Zara", "H&M", "Uniqlo", "Gap"],
                "line_category": {"singular": "brand", "plural": "brands"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Revenue ($ Billion)",
                "img_title": "Global Fast Fashion Brand Revenues (2019-2024)",
            },
            {
                "line_data": [
                    [15, 16, 18, 20, 22, 24],
                    [10, 11, 9, 11, 12, 13],
                    [8, 9, 12, 14, 15, 17],
                    [5, 6, 7, 8, 5, 3],
                ],
                "line_labels": ["Louis Vuitton", "Gucci", "Chanel", "Hermès"],
                "line_category": {"singular": "luxury brand", "plural": "luxury brands"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Revenue ($ Billion)",
                "img_title": "Luxury Brand Performance (2019-2024)",
            },
        ],
        "28 - Parenting & Child Development": [
            {
                "line_data": [
                    [45, 47, 50, 53, 56, 60],
                    [35, 37, 39, 33, 21, 25],
                    [25, 27, 29, 26, 33, 35],
                    [15, 16, 18, 41, 44, 47],
                ],
                "line_labels": ["Diaper Products", "Baby Food", "Toys", "Clothing"],
                "line_category": {"singular": "product category", "plural": "product categories"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Market Value ($ Billion)",
                "img_title": "Childcare Product Market Growth (2019-2024)",
            },
            {
                "line_data": [
                    [70, 73, 77, 81, 85, 90],
                    [50, 52, 55, 58, 61, 65],
                    [30, 36, 38, 32, 28, 30],
                    [20, 32, 34, 36, 38, 40],
                ],
                "line_labels": ["Early Education", "After-school Programs", "Online Learning", "Summer Camps"],
                "line_category": {"singular": "program type", "plural": "program types"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Enrollment (Million)",
                "img_title": "Child Development Program Enrollment (2019-2024)",
            },
        ],
        "29 - Architecture & Urban Planning": [
            {
                "line_data": [
                    [120, 125, 130, 135, 140, 145],
                    [100, 104, 108, 112, 116, 120],
                    [80, 84, 66, 78, 72, 88],
                    [60, 63, 87, 65, 54, 76],
                ],
                "line_labels": ["Skyscrapers", "Residential", "Commercial", "Mixed-use"],
                "line_category": {"singular": "building type", "plural": "building types"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "New Projects Started",
                "img_title": "Building Projects by Type (2019-2024)",
            },
            {
                "line_data": [
                    [70, 74, 78, 82, 86, 90],
                    [50, 53, 44, 46, 48, 50],
                    [40, 42, 34, 36, 38, 40],
                    [30, 32, 56, 59, 62, 66],
                ],
                "line_labels": ["New York", "Tokyo", "London", "Dubai"],
                "line_category": {"singular": "city", "plural": "cities"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Urban Development Spending ($ Billion)",
                "img_title": "City Infrastructure Investment (2019-2024)",
            },
        ],
        "30 - Gaming & Recreation": [
            {
                "line_data": [
                    [120, 130, 140, 150, 160, 170],
                    [100, 110, 120, 160, 140, 130],
                    [80, 85, 90, 76, 72, 80],
                    [60, 64, 68, 95, 100, 105],
                ],
                "line_labels": ["Sony", "Microsoft", "Nintendo", "Tencent"],
                "line_category": {"singular": "gaming company", "plural": "gaming companies"},
                "line_colors": ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Gaming Revenue ($ Billion)",
                "img_title": "Major Gaming Company Revenues (2019-2024)",
            },
            {
                "line_data": [
                    [60, 65, 70, 88, 82, 64],
                    [45, 48, 52, 56, 60, 74],
                    [30, 33, 36, 30, 28, 23],
                    [20, 22, 24, 39, 42, 45],
                ],
                "line_labels": ["Battle Royale", "MOBA", "RPG", "Simulation"],
                "line_category": {"singular": "game genre", "plural": "game genres"},
                "line_colors": ["#9B59B6", "#71A7DA", "#E67E22", "#2ECC71"],
                "x_labels": [2019, 2020, 2021, 2022, 2023, 2024],
                "x_label": "Year",
                "y_label": "Active Players (Million)",
                "img_title": "Popularity of Game Genres (2019-2024)",
            },
        ], 
    }
}


METADATA_HEATMAP = {
    "draw__7_heatmap__func_1": {
            "1 - Media & Entertainment": [
                {
                "heatmap_data": [
                    [80.5, 20.5, 55.5, 90.0, 60.0],
                    [30.5, 75.0, 45.5, 60.0, 80.0],
                    [90.0, 10.5, 80.0, 20.0, 70.5],
                    [80.0, 60.5, 30.0, 90.0, 59.5],
                    [77.5, 80.5, 66.5, 25.5, 95.5]
                ],
                "heatmap_category": {"singular": "rating score", "plural": "rating scores"},
                "x_labels": ["Titanic", "Star Wars", "The Lord of the Rings", "Snow White and the Seven Dwarfs", "The Lion King"],
                "y_labels": ["2005", "2010", "2015", "2020", "2025"],
                "x_label": "Movies",
                "y_label": "Rating Year",
                "img_title": "Correlation Between Movie Ratings and Rating Year"
            },
        ],
        "2 - Geography & Demography": [
            {
                "heatmap_data": [
                    [70.5, 82.0, 65.0, 90.0, 75.0],
                    [60.0, 55.0, 85.0, 80.0, 70.0],
                    [55.0, 78.0, 88.0, 60.0, 65.0],
                    [80.0, 68.0, 72.0, 85.0, 90.0],
                    [95.0, 75.0, 60.0, 70.0, 80.0]
                ],
                "heatmap_category": {"singular": "urbanization index", "plural": "urbanization indices"},
                "x_labels": ["Tokyo", "New York", "Paris", "São Paulo", "Lagos"],
                "y_labels": ["1990", "2000", "2010", "2020", "2030"],
                "x_label": "Cities",
                "y_label": "Year",
                "img_title": "Urbanization Indices Over Time in Major Global Cities"
            },
        ],
        "3 - Education & Academia": [
            {
                "heatmap_data": [
                    [85.0, 90.0, 78.0, 65.0, 88.0],
                    [75.0, 82.0, 80.0, 70.0, 83.0],
                    [92.0, 85.0, 88.0, 79.0, 91.0],
                    [80.0, 88.0, 76.0, 72.0, 85.0],
                    [88.0, 90.0, 84.0, 86.0, 89.0]
                ],
                "heatmap_category": {"singular": "graduation rate", "plural": "graduation rates"},
                "x_labels": ["Harvard", "Oxford", "Stanford", "Tsinghua", "ETH Zurich"],
                "y_labels": ["2015", "2016", "2017", "2018", "2019"],
                "x_label": "Universities",
                "y_label": "Graduation Year",
                "img_title": "Graduation Rates Across Leading Universities Over Five Years"
            },
        ],
        "4 - Business & Industry": [
            {
                "heatmap_data": [
                    [120.0, 150.0, 170.0, 200.0, 180.0],
                    [140.0, 130.0, 160.0, 190.0, 175.0],
                    [180.0, 175.0, 190.0, 210.0, 220.0],
                    [160.0, 155.0, 185.0, 200.0, 205.0],
                    [170.0, 165.0, 195.0, 220.0, 230.0]
                ],
                "heatmap_category": {"singular": "revenue (in billion USD)", "plural": "revenues (in billion USD)"},
                "x_labels": ["Apple", "Amazon", "Toyota", "Samsung", "Shell"],
                "y_labels": ["2018", "2019", "2020", "2021", "2022"],
                "x_label": "Companies",
                "y_label": "Fiscal Year",
                "img_title": "Annual Revenues of Global Corporations (2018–2022)"
            },
        ],
        "5 - Major & Course": [
            {
                "heatmap_data": [
                    [92.0, 85.0, 78.0, 80.0, 88.0],
                    [88.0, 82.0, 75.0, 83.0, 85.0],
                    [85.0, 80.0, 70.0, 78.0, 82.0],
                    [90.0, 88.0, 76.0, 85.0, 87.0],
                    [95.0, 92.0, 85.0, 90.0, 94.0]
                ],
                "heatmap_category": {"singular": "student satisfaction score", "plural": "student satisfaction scores"},
                "x_labels": ["Computer Science", "Psychology", "Business", "Mechanical Engineering", "Biology"],
                "y_labels": ["2017", "2018", "2019", "2020", "2021"],
                "x_label": "Majors",
                "y_label": "Survey Year",
                "img_title": "Student Satisfaction Scores by Major Over Recent Years"
            },
        ],
        "6 - Animal & Zoology": [
            {
                "heatmap_data": [
                    [80.0, 65.0, 75.0, 90.0, 85.0],
                    [70.0, 55.0, 60.0, 80.0, 75.0],
                    [85.0, 70.0, 80.0, 95.0, 88.0],
                    [78.0, 68.0, 72.0, 88.0, 82.0],
                    [90.0, 75.0, 85.0, 97.0, 92.0]
                ],
                "heatmap_category": {"singular": "habitat suitability score", "plural": "habitat suitability scores"},
                "x_labels": ["Savannah", "Rainforest", "Desert", "Wetlands", "Mountains"],
                "y_labels": ["Elephant", "Tiger", "Camel", "Crocodile", "Mountain Goat"],
                "x_label": "Habitat Type",
                "y_label": "Animal Species",
                "img_title": "Habitat Suitability Scores for Various Animal Species"
            },
        ],
        "7 - Plant & Botany": [
            {
                "heatmap_data": [
                    [60.0, 70.0, 80.0, 50.0, 65.0],
                    [75.0, 85.0, 90.0, 70.0, 80.0],
                    [55.0, 65.0, 75.0, 45.0, 60.0],
                    [85.0, 90.0, 95.0, 80.0, 88.0],
                    [70.0, 78.0, 82.0, 68.0, 75.0]
                ],
                "heatmap_category": {"singular": "growth success rate", "plural": "growth success rates"},
                "x_labels": ["Loamy Soil", "Sandy Soil", "Clay Soil", "Peaty Soil", "Silty Soil"],
                "y_labels": ["Wheat", "Rice", "Tomato", "Lavender", "Apple Tree"],
                "x_label": "Soil Type",
                "y_label": "Plant Species",
                "img_title": "Growth Success Rates of Different Plants Across Soil Types"
            },
        ],
        "8 - Biology & Chemistry": [
            {
                "heatmap_data": [
                    [98.0, 85.0, 75.0, 90.0, 88.0],
                    [80.0, 70.0, 65.0, 85.0, 82.0],
                    [90.0, 78.0, 70.0, 88.0, 86.0],
                    [85.0, 82.0, 72.0, 92.0, 89.0],
                    [95.0, 88.0, 80.0, 94.0, 91.0]
                ],
                "heatmap_category": {"singular": "enzyme activity level", "plural": "enzyme activity levels"},
                "x_labels": ["pH 4", "pH 5", "pH 6", "pH 7", "pH 8"],
                "y_labels": ["Amylase", "Protease", "Lipase", "Lactase", "Catalase"],
                "x_label": "pH Level",
                "y_label": "Enzyme Type",
                "img_title": "Enzyme Activity Levels Across Different pH Conditions"
            },
        ],
        "9 - Food & Nutrition": [
            {
                "heatmap_data": [
                    [320, 280, 350, 400, 370],
                    [250, 220, 300, 330, 310],
                    [400, 370, 420, 450, 430],
                    [280, 260, 340, 360, 340],
                    [360, 330, 390, 420, 400]
                ],
                "heatmap_category": {"singular": "calorie count", "plural": "calorie counts"},
                "x_labels": ["Breakfast", "Lunch", "Dinner", "Snack", "Dessert"],
                "y_labels": ["Salad", "Pasta", "Steak", "Sushi", "Burger"],
                "x_label": "Meal Type",
                "y_label": "Dish",
                "img_title": "Calorie Counts for Various Dishes Across Meal Types"
            },
        ],
        "10 - Space & Astronomy": [
            {
                "heatmap_data": [
                    [0.2, 0.5, 0.8, 1.0, 0.7],
                    [0.3, 0.6, 0.9, 1.2, 0.8],
                    [0.1, 0.4, 0.7, 0.9, 0.6],
                    [0.4, 0.7, 1.0, 1.3, 1.0],
                    [0.5, 0.8, 1.1, 1.4, 1.2]
                ],
                "heatmap_category": {"singular": "stellar luminosity (in solar units)", "plural": "stellar luminosities (in solar units)"},
                "x_labels": ["O-type", "B-type", "A-type", "F-type", "G-type"],
                "y_labels": ["Orion", "Andromeda", "Milky Way", "Triangulum", "Large Magellanic Cloud"],
                "x_label": "Star Type",
                "y_label": "Galaxy/Region",
                "img_title": "Average Stellar Luminosities by Star Type and Galaxy"
            },
        ],
        "11 - Sale & Merchandise": [
            {
                "heatmap_data": [
                    [1500, 1800, 2200, 1900, 2100],
                    [1300, 1600, 2000, 1700, 1850],
                    [1800, 2100, 2500, 2300, 2400],
                    [1400, 1700, 2150, 1800, 1950],
                    [1700, 2000, 2400, 2200, 2300]
                ],
                "heatmap_category": {"singular": "sales volume (units)", "plural": "sales volumes (units)"},
                "x_labels": ["Electronics", "Clothing", "Furniture", "Toys", "Groceries"],
                "y_labels": ["New York", "Los Angeles", "Chicago", "Houston", "Miami"],
                "x_label": "Product Category",
                "y_label": "City",
                "img_title": "Sales Volumes by Product Category and Major US Cities"
            },
        ],
        "12 - Market & Economy": [
            {
                "heatmap_data": [
                    [3.5, 2.8, 4.1, 3.7, 3.9],
                    [2.5, 1.9, 3.0, 2.7, 2.8],
                    [4.0, 3.2, 4.5, 4.1, 4.3],
                    [3.0, 2.4, 3.6, 3.2, 3.4],
                    [3.8, 3.1, 4.2, 3.9, 4.0]
                ],
                "heatmap_category": {"singular": "GDP growth rate (%)", "plural": "GDP growth rates (%)"},
                "x_labels": ["Technology", "Manufacturing", "Finance", "Healthcare", "Energy"],
                "y_labels": ["USA", "Germany", "China", "India", "Brazil"],
                "x_label": "Industry Sector",
                "y_label": "Country",
                "img_title": "GDP Growth Rates by Industry Sector Across Major Economies"
            },
        ],
        "13 - Sports & Athletics": [
            {
                "heatmap_data": [
                    [12.5, 11.8, 13.0, 12.2, 12.8],
                    [10.5, 9.8, 11.0, 10.3, 10.9],
                    [14.0, 13.2, 14.5, 13.8, 14.3],
                    [11.0, 10.2, 12.0, 11.3, 11.7],
                    [13.5, 12.8, 13.9, 13.1, 13.6]
                ],
                "heatmap_category": {"singular": "average sprint time (sec)", "plural": "average sprint times (sec)"},
                "x_labels": ["100m", "200m", "400m", "800m", "1500m"],
                "y_labels": ["USA", "Jamaica", "Kenya", "UK", "Japan"],
                "x_label": "Race Distance",
                "y_label": "Country",
                "img_title": "Average Sprint Times Across Countries and Distances"
            },
        ],
        "14 - Computing & Technology": [
            {
                "heatmap_data": [
                    [85.0, 90.0, 92.0, 88.0, 91.0],
                    [80.0, 85.0, 87.0, 83.0, 86.0],
                    [75.0, 80.0, 82.0, 78.0, 81.0],
                    [88.0, 92.0, 95.0, 90.0, 94.0],
                    [82.0, 86.0, 89.0, 84.0, 87.0]
                ],
                "heatmap_category": {"singular": "AI model accuracy (%)", "plural": "AI model accuracies (%)"},
                "x_labels": ["Image Classification", "Speech Recognition", "Translation", "Recommendation", "Medical Diagnosis"],
                "y_labels": ["Google", "Microsoft", "Meta", "Amazon", "IBM"],
                "x_label": "Application Area",
                "y_label": "Company",
                "img_title": "AI Model Accuracies Across Applications and Tech Companies"
            },
        ],
        "15 - Health & Medicine": [
            {
                "heatmap_data": [
                    [98.0, 95.0, 92.0, 97.0, 93.0],
                    [96.0, 93.0, 90.0, 95.0, 91.0],
                    [99.0, 97.0, 94.0, 98.0, 95.0],
                    [97.0, 94.0, 91.0, 96.0, 92.0],
                    [98.5, 96.0, 93.0, 97.5, 94.0]
                ],
                "heatmap_category": {"singular": "vaccine efficacy (%)", "plural": "vaccine efficacies (%)"},
                "x_labels": ["Influenza", "COVID-19", "HPV", "Hepatitis B", "Measles"],
                "y_labels": ["Pfizer", "Moderna", "Johnson & Johnson", "AstraZeneca", "Sanofi"],
                "x_label": "Disease",
                "y_label": "Vaccine Manufacturer",
                "img_title": "Vaccine Efficacies Across Diseases and Manufacturers"
            },
        ],
        "16 - Energy & Environment": [
            {
                "heatmap_data": [
                    [45.0, 60.0, 75.0, 50.0, 65.0],
                    [55.0, 70.0, 80.0, 60.0, 75.0],
                    [35.0, 50.0, 65.0, 40.0, 55.0],
                    [65.0, 80.0, 90.0, 70.0, 85.0],
                    [50.0, 65.0, 78.0, 55.0, 70.0]
                ],
                "heatmap_category": {"singular": "renewable energy share (%)", "plural": "renewable energy shares (%)"},
                "x_labels": ["Solar", "Wind", "Hydro", "Geothermal", "Biomass"],
                "y_labels": ["Germany", "China", "USA", "India", "Brazil"],
                "x_label": "Energy Source",
                "y_label": "Country",
                "img_title": "Share of Renewable Energy Sources by Country"
            },
        ],
        "17 - Travel & Expedition": [
            {
                "heatmap_data": [
                    [4.5, 3.8, 4.7, 4.2, 4.6],
                    [4.0, 3.5, 4.3, 3.9, 4.1],
                    [4.8, 4.2, 4.9, 4.5, 4.7],
                    [4.2, 3.7, 4.4, 4.0, 4.3],
                    [4.6, 4.0, 4.8, 4.4, 4.5]
                ],
                "heatmap_category": {"singular": "average traveler rating", "plural": "average traveler ratings"},
                "x_labels": ["Adventure", "Culture", "Nature", "Luxury", "Family"],
                "y_labels": ["Iceland", "Japan", "New Zealand", "Peru", "Italy"],
                "x_label": "Travel Theme",
                "y_label": "Destination Country",
                "img_title": "Average Traveler Ratings for Various Themes and Destinations"
            },
        ],
        "18 - Arts & Culture": [
            {
                "heatmap_data": [
                    [250, 180, 300, 220, 270],
                    [200, 150, 250, 180, 230],
                    [300, 230, 350, 280, 320],
                    [220, 170, 270, 200, 260],
                    [280, 210, 320, 250, 290]
                ],
                "heatmap_category": {"singular": "annual visitors (thousands)", "plural": "annual visitors (thousands)"},
                "x_labels": ["Modern Art", "Classical Art", "Photography", "Sculpture", "Folk Art"],
                "y_labels": ["MoMA", "Louvre", "Tate Modern", "Uffizi", "Rijksmuseum"],
                "x_label": "Exhibition Type",
                "y_label": "Museum",
                "img_title": "Annual Visitor Numbers by Exhibition Type and Museum"
            },
        ],
        "19 - Communication & Collaboration": [
            {
                "heatmap_data": [
                    [85.0, 90.0, 78.0, 88.0, 82.0],
                    [80.0, 85.0, 75.0, 83.0, 78.0],
                    [90.0, 95.0, 88.0, 92.0, 89.0],
                    [88.0, 92.0, 83.0, 90.0, 85.0],
                    [87.0, 91.0, 82.0, 89.0, 84.0]
                ],
                "heatmap_category": {"singular": "team productivity score", "plural": "team productivity scores"},
                "x_labels": ["Slack", "Zoom", "Microsoft Teams", "Asana", "Trello"],
                "y_labels": ["Engineering", "Marketing", "Sales", "Design", "HR"],
                "x_label": "Tool Used",
                "y_label": "Department",
                "img_title": "Team Productivity Scores Across Departments and Collaboration Tools"
            },
        ],
        "20 - Language & Linguistics": [
            {
                "heatmap_data": [
                    [92.0, 85.0, 78.0, 88.0, 80.0],
                    [88.0, 80.0, 72.0, 83.0, 76.0],
                    [95.0, 90.0, 85.0, 92.0, 87.0],
                    [90.0, 85.0, 80.0, 88.0, 83.0],
                    [93.0, 87.0, 82.0, 90.0, 85.0]
                ],
                "heatmap_category": {"singular": "comprehension accuracy (%)", "plural": "comprehension accuracies (%)"},
                "x_labels": ["English", "Mandarin", "Spanish", "Arabic", "French"],
                "y_labels": ["News Articles", "Literature", "Scientific Papers", "Legal Documents", "Social Media"],
                "x_label": "Language",
                "y_label": "Text Type",
                "img_title": "Comprehension Accuracy Across Languages and Text Types"
            },
        ],
        "21 - History & Archaeology": [
            {
                "heatmap_data": [
                    [85.0, 78.0, 90.0, 80.0, 88.0],
                    [75.0, 68.0, 82.0, 72.0, 79.0],
                    [92.0, 85.0, 95.0, 88.0, 93.0],
                    [80.0, 72.0, 85.0, 75.0, 82.0],
                    [88.0, 80.0, 92.0, 83.0, 89.0]
                ],
                "heatmap_category": {"singular": "artifact preservation score", "plural": "artifact preservation scores"},
                "x_labels": ["Pottery", "Sculptures", "Manuscripts", "Jewelry", "Weapons"],
                "y_labels": ["Ancient Egypt", "Maya Civilization", "Roman Empire", "Mesopotamia", "Indus Valley"],
                "x_label": "Artifact Type",
                "y_label": "Civilization",
                "img_title": "Preservation Scores of Artifacts Across Ancient Civilizations"
            },
        ],
        "22 - Weather & Climate": [
            {
                "heatmap_data": [
                    [25.0, 30.0, 28.0, 35.0, 32.0],
                    [20.0, 25.0, 22.0, 30.0, 27.0],
                    [15.0, 20.0, 18.0, 25.0, 22.0],
                    [10.0, 15.0, 12.0, 20.0, 18.0],
                    [5.0, 10.0, 8.0, 15.0, 12.0]
                ],
                "heatmap_category": {"singular": "average temperature (°C)", "plural": "average temperatures (°C)"},
                "x_labels": ["January", "April", "July", "October", "December"],
                "y_labels": ["Moscow", "Berlin", "Cairo", "Bangkok", "Sydney"],
                "x_label": "Month",
                "y_label": "City",
                "img_title": "Average Monthly Temperatures in Global Cities"
            },
        ],
        "23 - Transportation & Infrastructure": [
            {
                "heatmap_data": [
                    [90.0, 85.0, 92.0, 80.0, 88.0],
                    [75.0, 70.0, 78.0, 65.0, 73.0],
                    [85.0, 80.0, 88.0, 75.0, 82.0],
                    [80.0, 75.0, 83.0, 70.0, 78.0],
                    [88.0, 82.0, 90.0, 78.0, 85.0]
                ],
                "heatmap_category": {"singular": "infrastructure reliability score", "plural": "infrastructure reliability scores"},
                "x_labels": ["Highways", "Railways", "Airports", "Ports", "Bridges"],
                "y_labels": ["Japan", "Germany", "USA", "UK", "South Korea"],
                "x_label": "Infrastructure Type",
                "y_label": "Country",
                "img_title": "Infrastructure Reliability Scores by Type and Country"
            },
        ],
        "24 - Psychology & Personality": [
            {
                "heatmap_data": [
                    [70.0, 65.0, 80.0, 75.0, 68.0],
                    [60.0, 55.0, 70.0, 65.0, 58.0],
                    [85.0, 80.0, 90.0, 88.0, 82.0],
                    [75.0, 70.0, 85.0, 78.0, 72.0],
                    [80.0, 75.0, 88.0, 83.0, 77.0]
                ],
                "heatmap_category": {"singular": "trait prevalence score", "plural": "trait prevalence scores"},
                "x_labels": ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"],
                "y_labels": ["Engineers", "Artists", "Salespeople", "Teachers", "Healthcare Workers"],
                "x_label": "Personality Trait",
                "y_label": "Occupation",
                "img_title": "Prevalence of Personality Traits Across Professions"
            },
        ],
        "25 - Materials & Engineering": [
            {
                "heatmap_data": [
                    [1200, 1500, 2000, 1800, 1600],
                    [1000, 1300, 1700, 1500, 1400],
                    [1400, 1700, 2200, 2000, 1800],
                    [1100, 1400, 1900, 1700, 1550],
                    [1300, 1600, 2100, 1900, 1700]
                ],
                "heatmap_category": {"singular": "tensile strength (MPa)", "plural": "tensile strengths (MPa)"},
                "x_labels": ["Steel", "Aluminum", "Titanium", "Carbon Fiber", "Glass Fiber"],
                "y_labels": ["Bridge Design", "Aircraft Parts", "Car Frames", "Bicycle Frames", "Wind Turbines"],
                "x_label": "Material",
                "y_label": "Application",
                "img_title": "Tensile Strength of Materials Across Engineering Applications"
            },
        ],
        "26 - Philanthropy & Charity": [
            {
                "heatmap_data": [
                    [5.5, 6.2, 4.8, 7.0, 5.9],
                    [4.0, 4.5, 3.8, 5.2, 4.3],
                    [6.5, 7.0, 5.5, 7.8, 6.8],
                    [5.0, 5.8, 4.5, 6.5, 5.5],
                    [6.0, 6.7, 5.2, 7.2, 6.1]
                ],
                "heatmap_category": {"singular": "annual donation amount (million USD)", "plural": "annual donation amounts (million USD)"},
                "x_labels": ["Health", "Education", "Environment", "Hunger", "Arts"],
                "y_labels": ["Bill & Melinda Gates Foundation", "Wellcome Trust", "Ford Foundation", "Open Society Foundations", "Rockefeller Foundation"],
                "x_label": "Cause Area",
                "y_label": "Organization",
                "img_title": "Annual Donation Amounts by Major Foundations and Cause Areas"
            },
        ],
        "27 - Fashion & Apparel": [
            {
                "heatmap_data": [
                    [120, 150, 200, 180, 170],
                    [100, 130, 180, 160, 150],
                    [140, 170, 220, 200, 190],
                    [110, 140, 190, 170, 160],
                    [130, 160, 210, 190, 180]
                ],
                "heatmap_category": {"singular": "sales figure (thousands)", "plural": "sales figures (thousands)"},
                "x_labels": ["T-Shirts", "Jeans", "Dresses", "Jackets", "Shoes"],
                "y_labels": ["Zara", "H&M", "Uniqlo", "Nike", "Adidas"],
                "x_label": "Apparel Type",
                "y_label": "Brand",
                "img_title": "Sales Figures by Apparel Type and Global Fashion Brands"
            },
        ],
        "28 - Parenting & Child Development": [
            {
                "heatmap_data": [
                    [90.0, 85.0, 92.0, 88.0, 91.0],
                    [80.0, 75.0, 82.0, 78.0, 81.0],
                    [95.0, 90.0, 97.0, 93.0, 96.0],
                    [85.0, 80.0, 87.0, 83.0, 86.0],
                    [88.0, 83.0, 90.0, 86.0, 89.0]
                ],
                "heatmap_category": {"singular": "early learning success rate (%)", "plural": "early learning success rates (%)"},
                "x_labels": ["Language", "Math", "Motor Skills", "Social Skills", "Art"],
                "y_labels": ["Preschool A", "Preschool B", "Preschool C", "Preschool D", "Preschool E"],
                "x_label": "Developmental Area",
                "y_label": "Preschool",
                "img_title": "Early Learning Success Rates Across Preschools and Development Areas"
            },
        ],
        "29 - Architecture & Urban Planning": [
            {
                "heatmap_data": [
                    [70.0, 75.0, 85.0, 80.0, 78.0],
                    [65.0, 70.0, 80.0, 75.0, 73.0],
                    [85.0, 90.0, 95.0, 88.0, 87.0],
                    [75.0, 80.0, 90.0, 83.0, 82.0],
                    [80.0, 85.0, 92.0, 86.0, 85.0]
                ],
                "heatmap_category": {"singular": "sustainability score", "plural": "sustainability scores"},
                "x_labels": ["Green Roofs", "Passive Solar", "Bicycle Networks", "Urban Parks", "Water Recycling"],
                "y_labels": ["Amsterdam", "Copenhagen", "Singapore", "Vancouver", "Stockholm"],
                "x_label": "Urban Feature",
                "y_label": "City",
                "img_title": "Sustainability Scores of Urban Features in Leading Green Cities"
            },
        ],
        "30 - Gaming & Recreation": [
            {
                "heatmap_data": [
                    [4.8, 4.5, 4.9, 4.7, 4.6],
                    [4.2, 4.0, 4.5, 4.3, 4.1],
                    [4.9, 4.7, 5.0, 4.8, 4.9],
                    [4.5, 4.3, 4.7, 4.6, 4.4],
                    [4.7, 4.4, 4.8, 4.7, 4.5]
                ],
                "heatmap_category": {"singular": "average user rating", "plural": "average user ratings"},
                "x_labels": ["RPG", "Shooter", "Sports", "Strategy", "Adventure"],
                "y_labels": ["Steam", "PlayStation", "Xbox", "Nintendo Switch", "Mobile"],
                "x_label": "Game Genre",
                "y_label": "Platform",
                "img_title": "Average User Ratings by Game Genre and Gaming Platform"
            },
        ], 
    }
}


METADATA_PIE = {
    "draw__8_pie__func_1": {
        "1 - Media & Entertainment": [
            {
                "pie_data": [35, 25, 20, 15, 5],
                "pie_labels": ["Technology", "Healthcare", "Finance", "Education", "Others"],
                "pie_colors": ["#F4B8AE", "#ADD8F6", "#E6B7EC", "#C3E5BE", "#FECA57"],
                "pie_data_category": {"singular": "market share", "plural": "market shares"},
                "pie_label_category": {"singular": "market share category", "plural": "market share categories"},
                "img_title": "Market Share Distribution by Sector",
            },
        ],
        "2 - Geography & Demography": [
            # Source: United Nations/World Bank estimates for 2021
            {
                "pie_data": [59.4, 17.6, 9.4, 7.5, 5.5, 0.6],
                "pie_labels": ["Asia", "Africa", "Europe", "North America", "South America", "Oceania"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D"],
                "pie_data_category": {"singular": "continent", "plural": "continents"},
                "pie_label_category": {"singular": "continent", "plural": "continents"},
                "img_title": "World Population by Continent (2021)",
            },
        ],
        "3 - Education & Academia": [
            #https://data.cityofchicago.org/Education/Chicago-Public-Schools-Progress-Report-Cards-2011-/9xs2-f89t/about_data
            {
                "pie_data": [82, 16, 2],
                "pie_labels": ["High School", "Elementary School", "Middle School"],
                "pie_colors": ["#F4B8AE", "#ADD8F6", "#E6B7EC"],
                "pie_data_category": {"singular": "School Type ", "plural": "School Types"},
                "pie_label_category": {"singular": "School Type", "plural": "School Types"},
                "img_title": "School Type Distribution by School Level in Chicago",
            },
        ],
        "4 - Business & Industry": [
            # Source: Wikipedia/IMF for 2025
            {
                "pie_data": [63.6, 30.5, 5.9],
                "pie_labels": ["Services", "Industry", "Agriculture"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28"],
                "pie_data_category": {"singular": "economic sector", "plural": "economic sectors"},
                "pie_label_category": {"singular": "sector", "plural": "sectors"},
                "img_title": "Global GDP by Sector (2025)",
            },
        ],
        "5 - Major & Course": [
            # Source: National Center for Education Statistics (NCES) for the 2021–22 academic year
            {
                "pie_data": [19, 16, 16, 12, 37],
                "pie_labels": ["Business and Finance", "Consulting", "Engineering", "Media and Marketing", "Other"],
                "pie_colors": ["#F4B8AE", "#ADD8F6", "#E6B7EC", "#C3E5BE", "#FECA57"],
                "pie_data_category": {"singular": "Industry", "plural": "Industries"},
                "pie_label_category": {"singular": "Industry Category", "plural": "Industry Categories"},
                "img_title": "Job Sector Distribution Among Recent Northwestern Undergraduates",
            },
        ],
        "6 - Animal & Zoology": [
            # Source: Smithsonian/Our World in Data estimates of described species
            {
                "pie_data": [75, 8, 8, 9],
                "pie_labels": ["Insects", "Molluscs", "Arachnids", "All other animals"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"],
                "pie_data_category": {"singular": "animal group", "plural": "animal groups"},
                "pie_label_category": {"singular": "group", "plural": "groups"},
                "img_title": "Estimated Share of Animal Species by Group",
            },
        ],
        "7 - Plant & Botany": [
            # Source: nhpbs.org, en.uhomes.com
            {
                "pie_data": [80, 6, 3, 1],
                "pie_labels": ["Flowering plants (Angiosperms)", "Bryophytes (mosses & allies)", "Ferns and allies", "Gymnosperms (conifers & cycads)"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"],
                "pie_data_category": {"singular": "plant group", "plural": "plant groups"},
                "pie_label_category": {"singular": "group", "plural": "groups"},
                "img_title": "Global Plant Species by Type",
            },
        ],
        "8 - Biology & Chemistry": [
            # Source: geochemical analyses of the continental crust
            {
                "pie_data": [46.6, 27.7, 8.1, 5.0, 12.6],
                "pie_labels": ["Oxygen", "Silicon", "Aluminum", "Iron", "Other elements"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"],
                "pie_data_category": {"singular": "element", "plural": "elements"},
                "pie_label_category": {"singular": "element", "plural": "elements"},
                "img_title": "Composition of Earth's Crust by Element",
            },
        ],
        "9 - Food & Nutrition": [
            # Source: researchgate.net, worldpopulationreview.com
            {
                "pie_data": [50, 9, 8, 12, 21],
                "pie_labels": ["Grains (cereals)", "Sugars & sweeteners", "Vegetable oils & fats", "Animal products (meat/dairy/eggs)", "Other plant foods (fruits, vegetables, etc.)"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"],
                "pie_data_category": {"singular": "food category", "plural": "food categories"},
                "pie_label_category": {"singular": "food type", "plural": "food types"},
                "img_title": "Global Diet Composition by Food Group",
            },
        ],
        "10 - Space & Astronomy": [
            # Source: astronomy.swin.edu.au, ned.ipac.caltech.edu
            {
                "pie_data": [60, 20, 10, 10],
                "pie_labels": ["Spiral", "Lenticular", "Elliptical", "Irregular/Peculiar"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"],
                "pie_data_category": {"singular": "galaxy type", "plural": "galaxy types"},
                "pie_label_category": {"singular": "galaxy type", "plural": "galaxy types"},
                "img_title": "Galaxies by Type",
            },
        ],
        "11 - Sale & Merchandise": [
            # Source: U.S. Census and industry data for 2024
            {
                "pie_data": [21, 13, 12, 12, 10, 9, 7, 6, 5, 5],
                "pie_labels": ["Motor vehicles & parts", "Food & beverage stores", "General merchandise stores", "Food services & drinking places", "Non-store (online) retailers", "Gasoline stations", "Health & personal care stores", "Building materials & garden stores", "Electronics & appliance stores", "All other retail"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D", "#FFC658", "#FF6B9D", "#4ECDC4", "#45B7D1"],
                "pie_data_category": {"singular": "retail category", "plural": "retail categories"},
                "pie_label_category": {"singular": "retail category", "plural": "retail categories"},
                "img_title": "U.S. Retail Sales by Category (2024)",
            },
        ],
        "12 - Market & Economy": [
            # Source: theglobaleconomy.com
            {
                "pie_data": [26.3, 17.3, 15.0, 41.4],
                "pie_labels": ["United States", "China", "European Union", "Rest of world"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"],
                "pie_data_category": {"singular": "region/country", "plural": "regions/countries"},
                "pie_label_category": {"singular": "region", "plural": "regions"},
                "img_title": "Global GDP by Region (2023)",
            },
        ],
        "13 - Sports & Athletics": [
            # Source: worldpopulationreview.com, worldatlas.com
            {
                "pie_data": [3.5, 2.5, 2.2, 2.0, 1.0],
                "pie_labels": ["Soccer (Football)", "Cricket", "Basketball", "Field Hockey", "Tennis"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"],
                "pie_data_category": {"singular": "sport", "plural": "sports"},
                "pie_label_category": {"singular": "sport", "plural": "sports"},
                "img_title": "Most Popular Sports by Global Fan Base",
            },
        ],
        "14 - Computing & Technology": [
            # Source: IDC/StatCounter shipment estimates for 2023
            {
                "pie_data": [20, 16, 14, 9, 8, 33],
                "pie_labels": ["Samsung", "Apple", "Xiaomi", "vivo", "OPPO", "Other brands"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D"],
                "pie_data_category": {"singular": "smartphone vendor", "plural": "smartphone vendors"},
                "pie_label_category": {"singular": "vendor", "plural": "vendors"},
                "img_title": "Global Smartphone Market Share by Vendor (2023)",
            },
        ],
        "15 - Health & Medicine": [
            # Source: WHO/IHME Global Burden of Disease, 2019
            {
                "pie_data": [33, 20, 23, 18, 6],
                "pie_labels": ["Cardiovascular diseases", "Cancers", "Other non-communicable diseases", "Communicable (infectious) diseases", "Injuries (accidents/violence)"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"],
                "pie_data_category": {"singular": "cause of death", "plural": "causes of death"},
                "pie_label_category": {"singular": "cause", "plural": "causes"},
                "img_title": "Global Deaths by Cause (2019)",
            },
        ],
        "16 - Energy & Environment": [
            # Source: 2019 world energy consumption, per BP/IEA
            {
                "pie_data": [31.2, 27.2, 24.7, 6.9, 5.7, 4.3],
                "pie_labels": ["Oil", "Coal", "Natural Gas", "Hydropower", "Other Renewables", "Nuclear"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D"],
                "pie_data_category": {"singular": "energy source", "plural": "energy sources"},
                "pie_label_category": {"singular": "source", "plural": "sources"},
                "img_title": "Global Primary Energy Consumption by Source (2019)",
            },
        ],
        "17 - Travel & Expedition": [
            # Source: UNWTO for 2019
            {
                "pie_data": [50, 24, 16, 5, 5],
                "pie_labels": ["Europe", "Asia-Pacific", "Americas", "Africa", "Middle East"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"],
                "pie_data_category": {"singular": "region", "plural": "regions"},
                "pie_label_category": {"singular": "region", "plural": "regions"},
                "img_title": "International Tourism Arrivals by Region (2019)",
            },
        ],
        "18 - Arts & Culture": [
            # Source: Stronddo Art analysis of the Art Market (2022), citing Artprice data
            {
                "pie_data": [71.0, 14.0, 9.0, 6.0],
                "pie_labels": ["Paintings", "Drawings & Works on Paper", "Sculptures", "Other Artwork (Photography, Prints, Digital, etc.)"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"],
                "pie_data_category": {"singular": "art category", "plural": "art categories"},
                "pie_label_category": {"singular": "category", "plural": "categories"},
                "img_title": "Global Art Market Share by Category (2022)",
            },
        ],
        "19 - Communication & Collaboration": [
            # Source: SQ Magazine / 99Firms (2025), citing industry data on messaging app usage
            {
                "pie_data": [2000, 1260, 988, 574, 557, 550],
                "pie_labels": ["WhatsApp", "WeChat (Weixin)", "Facebook Messenger", "QQ", "Snapchat", "Telegram"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D"],
                "pie_data_category": {"singular": "messaging platform", "plural": "messaging platforms"},
                "pie_label_category": {"singular": "platform", "plural": "platforms"},
                "img_title": "Top Messaging Apps Worldwide by Monthly Active Users",
            },
        ],
        "20 - Language & Linguistics": [
            # Source: Ethnologue 2025 via Babbel Magazine
            {
                "pie_data": [1300, 486, 380, 362, 345, 237, 236, 148, 123, 118],
                "pie_labels": ["Chinese (Mandarin)", "Spanish", "English", "Arabic", "Hindi", "Bengali", "Portuguese", "Russian", "Japanese", "Punjabi (Lahnda)"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D", "#FFC658", "#FF6B9D", "#4ECDC4", "#45B7D1"],
                "pie_data_category": {"singular": "language", "plural": "languages"},
                "pie_label_category": {"singular": "language", "plural": "languages"},
                "img_title": "Top 10 Languages by Number of Native Speakers",
            },
        ],
        "21 - History & Archaeology": [
            # Source: UNESCO's World Heritage Centre statistics (as compiled in the World Heritage Sites by Country ranking, updated Feb 2025)
            {
                "pie_data": [60, 59, 54, 53, 50, 43, 35, 35, 32, 28],
                "pie_labels": ["Italy", "China", "Germany", "France", "Spain", "India", "Mexico", "United Kingdom", "Russia", "Iran"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D", "#FFC658", "#FF6B9D", "#4ECDC4", "#45B7D1"],
                "pie_data_category": {"singular": "country", "plural": "countries"},
                "pie_label_category": {"singular": "country", "plural": "countries"},
                "img_title": "Top 10 Countries by Number of UNESCO World Heritage Sites",
            },
        ],
        "22 - Weather & Climate": [
            # Source: IPCC and World Resources Institute data (2019) as summarized by Our World in Data
            {
                "pie_data": [24.2, 18.4, 17.5, 16.2, 13.6, 5.2, 3.2],
                "pie_labels": ["Energy Use in Industry", "Agriculture, Forestry & Land Use", "Energy Use in Buildings", "Transportation", "Other Fuel Combustion & Fugitive Energy", "Industrial Processes (Chemicals, Cement, etc.)", "Waste Management"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D", "#FFC658"],
                "pie_data_category": {"singular": "emission sector", "plural": "emission sectors"},
                "pie_label_category": {"singular": "sector", "plural": "sectors"},
                "img_title": "Global Greenhouse Gas Emissions by Sector (2019)",
            },
        ],
        "23 - Transportation & Infrastructure": [
            # Source: International Energy Agency and BCG studies referenced in a 2024 transport decarbonization report
            {
                "pie_data": [45, 29, 12, 11, 3],
                "pie_labels": ["Road Transport – Passenger", "Road Transport – Freight", "Aviation", "Shipping (Marine)", "Other Transport (Rail, Pipeline, etc.)"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"],
                "pie_data_category": {"singular": "transport mode", "plural": "transport modes"},
                "pie_label_category": {"singular": "mode", "plural": "modes"},
                "img_title": "Share of Global Transport CO₂ Emissions by Mode",
            },
        ],
        "24 - Psychology & Personality": [
            # Source: Myers–Briggs manual data via Crown Counseling and PersonalityMax (circa 1990s, reaffirmed by later analyses)
            {
                "pie_data": [13.8, 12.3, 11.6, 8.8, 8.7, 8.5, 8.1, 5.4, 4.4, 4.3, 3.3, 3.2, 2.5, 2.1, 1.8, 1.5],
                "pie_labels": ["ISFJ", "ESFJ", "ISTJ", "ISFP", "ESTJ", "ESFP", "ENFP", "ISTP", "INFP", "ESTP", "INTP", "ENTP", "ENFJ", "INTJ", "ENTJ", "INFJ"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D", "#FFC658", "#FF6B9D", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE"],
                "pie_data_category": {"singular": "MBTI type", "plural": "MBTI types"},
                "pie_label_category": {"singular": "personality type", "plural": "personality types"},
                "img_title": "Distribution of Myers–Briggs Personality Types (US Adult Population)",
            },
        ],
        "25 - Materials & Engineering": [
            # Source: Textile Exchange's Materials Market Report 2024
            {
                "pie_data": [57, 19, 18, 6],
                "pie_labels": ["Polyester Fiber (synthetic)", "Cotton Fiber (natural)", "Other Fibers (nylon, rayon, wool, etc.)", "Manmade Cellulosic Fiber (viscose, etc.)"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"],
                "pie_data_category": {"singular": "fiber type", "plural": "fiber types"},
                "pie_label_category": {"singular": "fiber", "plural": "fibers"},
                "img_title": "Global Material Production by Type (2023)",
            },
        ],
        "26 - Philanthropy & Charity": [
            # Source: Giving USA 2023 report (Indiana University Lilly Family School of Philanthropy)
            {
                "pie_data": [26.2, 15.9, 15.7, 14.4, 11.3, 10.2, 5.4, 4.5, 3.8],
                "pie_labels": ["Religion", "Human Services", "Education", "Foundations (Grantmaking)", "Public-Society Benefit", "Health", "International Affairs", "Arts, Culture & Humanities", "Environment & Animals"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D", "#FFC658", "#FF6B9D", "#4ECDC4"],
                "pie_data_category": {"singular": "recipient sector", "plural": "recipient sectors"},
                "pie_label_category": {"singular": "sector", "plural": "sectors"},
                "img_title": "U.S. Charitable Giving by Recipient Type (2022)",
            },
        ],
        "27 - Fashion & Apparel": [
            # Source: Textile Exchange – Preferred Fiber & Materials Report 2022 and 2024 updates
            {
                "pie_data": [54, 24, 15, 6, 1],
                "pie_labels": ["Polyester (synthetic)", "Cotton (natural)", "Other Synthetics (e.g. nylon, acrylic)", "Manmade Cellulosics (viscose, etc.)", "Wool and Other Naturals"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"],
                "pie_data_category": {"singular": "fiber type", "plural": "fiber types"},
                "pie_label_category": {"singular": "fiber", "plural": "fibers"},
                "img_title": "Global Textile Fiber Market Share by Fiber Type",
            },
        ],
        "28 - Parenting & Child Development": [
            # Source: U.S. Census Bureau Household Pulse Survey, Sept–Dec 2022
            {
                "pie_data": [61.0, 21.8, 8.4, 5.4, 5.4, 5.1, 3.0, 1.0],
                "pie_labels": ["No formal arrangement (parent-only care)", "Care by a relative (e.g. grandparent)", "Daycare center", "Non-relative babysitter or nanny", "Nursery or preschool", "Before/after-school program", "Family day care home", "Head Start program"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D", "#FFC658", "#FF6B9D"],
                "pie_data_category": {"singular": "child care arrangement", "plural": "child care arrangements"},
                "pie_label_category": {"singular": "arrangement", "plural": "arrangements"},
                "img_title": "Child Care Arrangements for U.S. Parents (2022)",
            },
        ],
        "29 - Architecture & Urban Planning": [
            # Source: UN FAO and HYDE land-use data as synthesized by Our World in Data
            {
                "pie_data": [38, 12, 37, 11, 1, 1],
                "pie_labels": ["Agricultural Land – Pasture & Feed", "Agricultural Land – Crops for Food", "Forests", "Shrubs & Grasslands", "Urban/Built-up Areas", "Freshwater (Lakes/Rivers)"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D"],
                "pie_data_category": {"singular": "land use category", "plural": "land use categories"},
                "pie_label_category": {"singular": "land use", "plural": "land uses"},
                "img_title": "Global Land Use of Habitable Land by Category",
            },
        ],
        "30 - Gaming & Recreation": [
            # Source: Entertainment Software Association
            {
                "pie_data": [48.2, 28.5, 23.3],
                "pie_labels": ["Mobile", "Console", "PC"],
                "pie_colors": ["#0088FE", "#00C49F", "#FFBB28"],
                "pie_data_category": {"singular": "gaming platform", "plural": "gaming platforms"},
                "pie_label_category": {"singular": "platform", "plural": "platforms"},
                "img_title": "Video Game Platform Market Share",
            },
        ],
        }
    }