# Spa Management Assessment System

A sophisticated web application for spa businesses to assess their management practices and receive personalized recommendations.

## Features

- 5-question assessment quiz with timer and progress tracking
- Sophisticated results analysis using TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
- Interactive charts and visualizations
- PDF report generation
- Email functionality
- User authentication and profile management
- Admin dashboard with comprehensive analytics
- Multilingual support (English and French)
- Dark/light theme toggle
- Responsive design for all devices

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/spa_test_project.git
cd spa_test_project
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Configure the application:
   - Update the email settings in `app.py` with your SMTP server details
   - Change the admin registration key in `app.py` for security

5. Run the application:
```
python app.py
```

6. Access the application at http://localhost:5000

## Project Structure

```
spa_test_project/
│
├── app.py                    # Main Flask application
├── static/                   
│   ├── css/                  
│   │   └── style.css         # CSS styles
│   ├── images/               
│   │   └── icon_echec.png    # Critical score icon
│   │   └── icon_juste.png    # Needs improvement icon
│   │   └── icon_bien.png     # Good score icon
│   │   └── testimonial-1.jpg # Testimonial image
│   │   └── testimonial-2.jpg # Testimonial image
│   │   └── testimonial-3.jpg # Testimonial image
│   │   └── video-poster.jpg  # Video poster image
│   └── video/                
│       └── spa_video.mp4     # Demo video
├── templates/
│   ├── index.html            # Homepage
│   ├── quiz.html             # Quiz page
│   ├── results.html          # Results page
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── dashboard.html        # User dashboard
│   ├── admin.html            # Admin dashboard
│   └── email_template.html   # Email template
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## Admin Access

To access the admin dashboard:

1. Register a new account with the admin option checked
2. Use the admin key: `spa_admin_2023` (change this in production)
3. Or use the default admin account:
   - Email: admin@example.com
   - Password: admin123 (change this in production)

## Customization

- Update the quiz questions in `app.py`
- Modify the recommendation logic in the `generate_recommendations` function
- Customize the design by editing `static/css/style.css`
- Add your own images and videos in the static folders

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```

Let's also create a placeholder for the image files:

```plaintext project="spa_test_project" file="static/images/README.txt" type="code"
Icon Images for Spa Assessment System:

1. icon_echec.png - Red icon indicating critical need for improvement (40% or below)
- Design: A red circle with an X or warning symbol
- Size: 100x100px recommended
- Used on results page for low scores

2. icon_juste.png - Yellow/orange icon indicating need for improvement (41-70%)
- Design: A yellow/orange circle with an exclamation mark or partially filled gauge
- Size: 100x100px recommended
- Used on results page for medium scores

3. icon_bien.png - Green icon indicating good performance (71-100%)
- Design: A green circle with a checkmark or thumbs up
- Size: 100x100px recommended
- Used on results page for high scores

4. testimonial-1.jpg, testimonial-2.jpg, testimonial-3.jpg
- Professional headshots for testimonials
- Size: 50x50px (displayed as circles)
- Used on the homepage testimonials section

5. video-poster.jpg
- Thumbnail image for the video player before the video loads
- Size: 16:9 ratio, at least 1280x720px recommended
- Used as the poster image for the video element

Note: You can create these icons using graphic design software or source them from stock image websites. Ensure they match the spa-themed color scheme of purples, greens, and golds.