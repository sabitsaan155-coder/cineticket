from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Country(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=80, unique=True)
    code = models.CharField(max_length=12, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Studio(models.Model):
    name = models.CharField(max_length=160, unique=True)
    slug = models.SlugField(max_length=180, unique=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="studios",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Person(models.Model):
    full_name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="people",
    )
    birth_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class AgeRating(models.Model):
    code = models.CharField(max_length=10, unique=True)  # 6+, 12+, 16+, 18+
    min_age = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(21)])

    class Meta:
        ordering = ["min_age"]

    def __str__(self):
        return self.code


class FormatType(models.Model):
    name = models.CharField(max_length=40, unique=True)  # 2D / 3D / IMAX
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Amenity(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Cinema(models.Model):
    name = models.CharField(max_length=160, unique=True)
    slug = models.SlugField(max_length=180, unique=True)
    city = models.CharField(max_length=120, default="Алматы")
    address = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Hall(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name="halls")
    format_type = models.ForeignKey(
        FormatType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="halls",
    )
    name = models.CharField(max_length=60)
    capacity = models.PositiveSmallIntegerField(default=80)

    class Meta:
        ordering = ["cinema__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["cinema", "name"], name="unique_hall_name_per_cinema"),
        ]

    def __str__(self):
        return f"{self.cinema.name} / {self.name}"


class HallAmenity(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name="amenities_link")
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, related_name="halls_link")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["hall", "amenity"], name="unique_amenity_per_hall"),
        ]

    def __str__(self):
        return f"{self.hall} / {self.amenity}"


class Movie(models.Model):
    class Status(models.TextChoices):
        NOW = "now", "В прокате"
        SOON = "soon", "Скоро"

    title = models.CharField(max_length=220, unique=True)
    slug = models.SlugField(max_length=240, unique=True)
    original_title = models.CharField(max_length=220, blank=True)
    description = models.TextField()
    poster_url = models.URLField(blank=True)
    duration_min = models.PositiveSmallIntegerField(validators=[MinValueValidator(30), MaxValueValidator(300)])
    release_year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NOW)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movies",
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movies",
    )
    studio = models.ForeignKey(
        Studio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movies",
    )
    age_rating = models.ForeignKey(
        AgeRating,
        on_delete=models.PROTECT,
        related_name="movies",
    )
    genres = models.ManyToManyField(Genre, related_name="movies", blank=True)
    cast = models.ManyToManyField(Person, through="MovieCast", related_name="movies", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-release_year", "title"]

    def __str__(self):
        return self.title


class MovieCast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="cast_items")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="cast_items")
    role_name = models.CharField(max_length=120, blank=True)
    position = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["movie", "position", "person__full_name"]
        constraints = [
            models.UniqueConstraint(fields=["movie", "person"], name="unique_person_per_movie_cast"),
        ]

    def __str__(self):
        return f"{self.movie.title} / {self.person.full_name}"


class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="screenings")
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name="screenings")
    start_at = models.DateTimeField()
    run_from = models.DateField()
    run_to = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_at"]
        constraints = [
            models.UniqueConstraint(fields=["hall", "start_at"], name="unique_hall_screening_time"),
        ]

    def clean(self):
        if self.run_from and self.run_to and self.run_from > self.run_to:
            raise ValidationError({"run_to": "Дата окончания проката должна быть не раньше даты начала."})

        if self.start_at:
            screening_date = timezone.localtime(self.start_at).date()
            if self.run_from and screening_date < self.run_from:
                raise ValidationError({"start_at": "Сеанс не может быть раньше даты начала проката."})
            if self.run_to and screening_date > self.run_to:
                raise ValidationError({"start_at": "Сеанс не может быть позже даты окончания проката."})

    def __str__(self):
        return f"{self.movie.title} / {self.start_at:%d.%m.%Y %H:%M}"


class TicketCategory(models.Model):
    code = models.CharField(max_length=20, unique=True)  # adult/student/child
    title = models.CharField(max_length=40, unique=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class TicketPrice(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ticket_prices")
    category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE, related_name="movie_prices")
    price = models.PositiveIntegerField(validators=[MinValueValidator(100)])

    class Meta:
        ordering = ["movie__title", "category__title"]
        constraints = [
            models.UniqueConstraint(fields=["movie", "category"], name="unique_ticket_price_per_category"),
        ]

    def __str__(self):
        return f"{self.movie.title} / {self.category.title}: {self.price}"
