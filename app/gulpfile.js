var gulp = require('gulp'),
    sass = require('gulp-sass'),
    del = require('del'),
    minifyCSS = require('gulp-minify-css'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify');

gulp.task('sass', function() {
  gulp.src('./src/sass/application.scss')
    .pipe(sass())
    .pipe(minifyCSS({keepBreaks:true}))
    .pipe(gulp.dest('./dist/css'))
});

gulp.task('js', function() {
  gulp.src('./src/js/*.js')
    .pipe(concat('app.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest('./dist/js'));
});

gulp.task('fonts', function() {
  gulp.src('./src/font/**/*.{ttf,woff,eot,svg}')
    .pipe(gulp.dest('./dist/font'))
})

gulp.task('assets', ['sass', 'js', 'fonts']);

gulp.task('clean', function() {
  del([
    'dist/**',
    ])
});