var gulp = require('gulp');
var typescript = require('gulp-typescript');
var merge2 = require('merge2');
var uglify = require('gulp-uglify')
var pump = require('pump')
var concat = require('gulp-concat')

var paths = {
    lambda: ['./src/*.ts'],
  src: ['./src/www/*.ts'],
  out: ['./*.js'],
  controllers: ['./src/www/controllers/**/*.ts'],
  services: ['./src/www/services/**/*.ts']
};

gulp.task('default', ['lambda', 'scripts', 'controllers', 'services']);

gulp.task('lambda', function () {
    var tsResult = gulp.src(paths.lambda)
        .pipe(typescript({}))
        .js
        .pipe(gulp.dest('./'));
});

gulp.task('scripts', function () {
    var tsResult = gulp.src(paths.src)
        .pipe(typescript({}))
        .js
        .pipe(gulp.dest('./www/js/'));
});

gulp.task('controllers', function () {
    var tsResult = gulp.src(paths.controllers)
        .pipe(typescript({}));
 
    return merge2([
        tsResult.js
        .pipe(concat('controllers.all.js'))
        .pipe(gulp.dest('./www/js/'))
    ]);
});

gulp.task('services', function () {
    var tsResult = gulp.src(paths.services)
        .pipe(typescript({}));
 
    return merge2([
        tsResult.js
        .pipe(concat('services.all.js'))
        .pipe(gulp.dest('./www/js/'))
    ]);
});

gulp.task('watch', function() {
  gulp.watch(paths.lambda, ['lambda']);
  gulp.watch(paths.scripts, ['scripts']);
  gulp.watch(paths.controllers, ['controllers']);
  gulp.watch(paths.services, ['services']);
});

gulp.task('compress', function(cb) {
    pump([
        gulp.src(paths.out),
        uglify(),
        gulp.dest('./compressed/')
    ])
})