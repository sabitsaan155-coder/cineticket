from django.contrib import admin

from .models import (
    AgeRating,
    Amenity,
    Cinema,
    Country,
    FormatType,
    Genre,
    Hall,
    HallAmenity,
    Language,
    Movie,
    MovieCast,
    Person,
    Screening,
    Studio,
    TicketCategory,
    TicketPrice,
)


@admin.action(description="Пометить как 'В прокате'")
def mark_as_now(modeladmin, request, queryset):
    queryset.update(status=Movie.Status.NOW)


@admin.action(description="Пометить как 'Скоро'")
def mark_as_soon(modeladmin, request, queryset):
    queryset.update(status=Movie.Status.SOON)


class MovieCastInline(admin.TabularInline):
    model = MovieCast
    extra = 1
    autocomplete_fields = ("person",)


class TicketPriceInline(admin.TabularInline):
    model = TicketPrice
    extra = 1
    autocomplete_fields = ("category",)


class HallInline(admin.TabularInline):
    model = Hall
    extra = 1
    fields = ("name", "format_type", "capacity")
    autocomplete_fields = ("format_type",)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "release_year",
        "age_rating",
        "country",
        "duration_min",
        "created_at",
    )
    search_fields = ("title", "original_title", "description", "studio__name")
    list_filter = ("status", "release_year", "age_rating", "country", "language", "genres")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "genre_list", "cast_count")
    filter_horizontal = ("genres",)
    autocomplete_fields = ("country", "language", "studio", "age_rating")
    inlines = (MovieCastInline, TicketPriceInline)
    actions = (mark_as_now, mark_as_soon)
    fieldsets = (
        (
            "Основное",
            {
                "fields": (
                    "title",
                    "slug",
                    "original_title",
                    "description",
                    "poster_url",
                    "status",
                )
            },
        ),
        (
            "Характеристики",
            {"fields": ("duration_min", "release_year", "age_rating", "genres")},
        ),
        ("Производство", {"fields": ("country", "language", "studio")}),
        ("Служебное", {"fields": ("created_at", "genre_list", "cast_count")}),
    )

    @admin.display(description="Жанры")
    def genre_list(self, obj):
        return ", ".join(obj.genres.values_list("name", flat=True)) or "—"

    @admin.display(description="Кол-во актеров")
    def cast_count(self, obj):
        return obj.cast_items.count()


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "address", "slug")
    search_fields = ("name", "city", "address")
    list_filter = ("city",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (HallInline,)


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "cinema", "format_type", "capacity")
    search_fields = ("name", "cinema__name")
    list_filter = ("cinema", "format_type")
    autocomplete_fields = ("cinema", "format_type")


@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = ("movie", "hall", "cinema_name", "start_at", "run_from", "run_to", "created_at")
    search_fields = ("movie__title", "hall__name", "hall__cinema__name")
    list_filter = ("hall__cinema", "hall", "movie__status", "run_from", "run_to")
    readonly_fields = ("created_at", "cinema_name")
    autocomplete_fields = ("movie", "hall")

    @admin.display(description="Кинотеатр")
    def cinema_name(self, obj):
        return obj.hall.cinema.name


@admin.register(TicketPrice)
class TicketPriceAdmin(admin.ModelAdmin):
    list_display = ("movie", "category", "price")
    search_fields = ("movie__title", "category__title")
    list_filter = ("category", "movie__status", "movie__country")
    autocomplete_fields = ("movie", "category")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    list_filter = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name", "country", "birth_date")
    search_fields = ("full_name",)
    list_filter = ("country",)
    prepopulated_fields = {"slug": ("full_name",)}
    autocomplete_fields = ("country",)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    list_filter = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "slug")
    search_fields = ("name", "code")
    list_filter = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "slug")
    search_fields = ("name",)
    list_filter = ("country",)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("country",)


@admin.register(FormatType)
class FormatTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    list_filter = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    list_filter = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(HallAmenity)
class HallAmenityAdmin(admin.ModelAdmin):
    list_display = ("hall", "amenity")
    search_fields = ("hall__name", "hall__cinema__name", "amenity__name")
    list_filter = ("amenity", "hall__cinema")
    autocomplete_fields = ("hall", "amenity")


@admin.register(MovieCast)
class MovieCastAdmin(admin.ModelAdmin):
    list_display = ("movie", "person", "role_name", "position")
    search_fields = ("movie__title", "person__full_name", "role_name")
    list_filter = ("movie",)
    autocomplete_fields = ("movie", "person")


@admin.register(AgeRating)
class AgeRatingAdmin(admin.ModelAdmin):
    list_display = ("code", "min_age")
    search_fields = ("code",)
    list_filter = ("min_age",)


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "code")
    search_fields = ("title", "code")
    list_filter = ("title",)
