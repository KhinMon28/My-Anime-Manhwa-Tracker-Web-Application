# My Anime/Manhwa Tracker

#### Video Demo:  <[URL HERE](https://youtu.be/Q_rQKrV5AsQ?si=ci8AxtLo0Pm443hM)>

#### Description:
## Project Overview:
The Anime/Manhwa Tracker is a web-based application that allows users to manage and explore their personal collections of anime and manhwa. Users can add new series to their lists, track their watching or reading progress, rate entries, assign multiple genres, upload optional images, and add comments. The platform also provides personalized recommendations based on users’ preferences, using both local data and the Jikan API. Designed with both aesthetics and usability in mind, the application ensures each user has a private, personalized experience while offering a clean and visually appealing interface.

This project was built using Flask for the backend, SQLite for the database, and HTML/CSS/Jinja2 templates for the frontend. It emphasizes responsive design, user security, and intuitive navigation. Features like dark mode, progress badges, search, filtering, sorting, and genre-based recommendations enhance usability, making it an ideal tool for anime and manhwa enthusiasts.

## File Structure and Functionality:
The application is organized into static assets, templates, and backend code. The static folder contains the style.css file, which defines the layout, typography, colors, and responsive card design, as well as hover effects, badges for progress status, buttons, forms, and a dark mode toggle. The favicon, favicon.png, enhances branding and browser tab recognition.

All HTML pages extend a single base template, layout.html, which provides the site’s header, navigation, dark mode toggle, and consistent styling across pages. Templates include:

- index.html: The homepage displays all user-added entries in card format, with title, type, rating, tags, comments, and optional images. Users can search, filter by genre or progress, and sort entries alphabetically or by rating. Pagination ensures a smooth browsing experience.

- add.html: Provides a form for adding new anime or manhwa, including multiple genres, type, progress, rating, image URL, and comments.

- edit.html: Similar to add.html, this page allows editing of existing entries with pre-populated values and multi-genre support. Only the owner of an entry can edit it.

- login.html and signup.html: Manage secure user authentication with password hashing, input validation, and flash messages for feedback.

- recommendations.html: Displays recommendations based on the user’s top-rated genres. Suggestions include local entries not yet in the user’s collection and external entries fetched from the Jikan API.

This structure ensures a clear separation of concerns and consistent user experience.

## Database Structure:
The application uses SQLite with two main tables:

- users: Stores user credentials, with fields for a unique username and hashed password.

- anime: Stores anime/manhwa entries, including title, type, progress status, rating, optional image URL, comments, genres (as a comma-separated string), and user_id to link entries to their owners.

The user_id foreign key ensures that each user sees only their own collection, enabling private, personalized lists. Queries filter entries based on the logged-in user, maintaining data integrity and security.

## Backend Functionality:
The backend, powered by Flask, handles all core functionality:

- Index (/): Displays user entries with search, filter, and sorting capabilities, including pagination.

- Add (/add): Handles POST requests to create new entries and stores them in the database, linking each entry to the logged-in user.

- Edit (/edit/<id>): Allows users to update their entries; ownership verification prevents unauthorized edits.

- Delete (/delete/<id>): Deletes a user’s entry, ensuring only the owner can perform this action.

- Signup (/signup) and Login (/login): Securely handle user registration and authentication using hashed passwords. Flash messages provide instant feedback for errors or successes.

- Logout (/logout): Clears session data to log users out safely.

- Recommendations (/recommendations): Generates personalized recommendations based on the top five genres from a user’s rated entries. Recommendations are sourced both locally and externally via the Jikan API, and scored based on genre overlap and ratings.

The backend ensures robust, secure functionality while maintaining simplicity and scalability.

## Design decisions:
Several thoughtful design choices enhance both usability and security. Users can only access their own data, preventing cross-account visibility. Password hashing and session management protect sensitive information. The interface uses flexbox layouts, hover effects, and visually distinct progress badges to make browsing intuitive. Dark mode is implemented with a toggle switch and stored in localStorage for persistence. Tags allow both filtering and recommendation generation, providing a dynamic and personalized experience.

The recommendation system combines user-specific preferences with external API data, enabling meaningful suggestions without overwhelming the interface. Pagination, search, and sort features enhance usability for large collections. Forms are designed with validation and clear labeling, ensuring ease of use.

## Future Improvements:
Future enhancements could include:

- More sophisticated recommendation algorithms using collaborative filtering or machine learning.

- Deeper integration with external APIs for automatic data updates.

- Social features, such as sharing lists or following friends.

- Additional filters for studio, release year, or author for more precise management.

These features would further improve personalization, engagement, and overall utility!

## Conclusion:
The Anime/Manhwa Tracker is a comprehensive, user-centric application that allows anime and manhwa enthusiasts to manage, track, and discover new content. Its combination of secure authentication, private collections, intuitive design, responsive interface, and personalized recommendations provides a robust and engaging user experience. The project demonstrates clean code structure, thoughtful design, and practical use of Flask, SQLite, and frontend technologies, making it both functional and expandable for future development.

