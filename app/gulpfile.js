var gulp = require('gulp');
var sass = require('gulp-sass');
var del = require('del');

gulp.task('sass', function() {
  gulp.src('./src/sass/application.scss')
    .pipe(sass())
    .pipe(gulp.dest('./dist/css'))
});

gulp.task('clean', function() {
  del([
    'dist/**',
    ])
});