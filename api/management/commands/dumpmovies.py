import asyncio
from dataclasses import dataclass
from typing import List, Tuple

import bs4
from api.models import Actor, Movie
from api.utils import send_request_async, url_join
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand

CSFD_URL = "https://www.csfd.cz"
CSFD_BEST_MOVIES_PATH = "zebricky/nejlepsi-filmy/?show=complete​"


@dataclass
class PageData:
    """
    Example:
        <a href="/zebricky/filmy/nejlepsi/">1</a>
        <a href="/zebricky/filmy/nejlepsi/?from=100">100</a>
        <a href="/zebricky/filmy/nejlepsi/?from=200">200</a>
    """

    number: int
    path: str

    @classmethod
    def from_node(cls, node: bs4.element.Tag):
        page = int(node.getText())
        path = node.attrs["href"]
        return PageData(page, path)


@dataclass
class ActorData:
    fullName: str
    path: str
    id: int

    @classmethod
    def from_node(cls, node: bs4.element.Tag):
        fullName = node.getText()
        path = node.attrs["href"]
        return ActorData(fullName, path, -1)

    def as_dict(self):
        split_name = self.fullName.split(" ")
        result = dict(
            givenName=split_name[0], lastName=split_name[-1], fullName=self.fullName, url=url_join(CSFD_URL, self.path)
        )
        if self.id > 0:
            result["id"] = self.id
        return result


@dataclass
class MovieData:
    """
    Example:

        <div class="box-content box-content-striped-articles">
        <p class="film-origins-genres"><span class="info">USA, Drama / Životopisný</span></p>
        <p class="film-creators">Režie: <a href="/tvurce/3004-penny-marshall/">Penny Marshall</a></p><p class="film-creators">Hrají: <a href="/tvurce/98-robert-de-niro/">Robert De Niro</a>, <a href="/tvurce/510-robin-williams/">Robin Williams</a></p>
                        <div class="article-toplist-rating">
                                        <div class="rating-average red">87,0%</div>
                                        <div class="rating-total">
                                                17&nbsp;427 <span>hodnocení</span>
                                                <span class="rating-mobile">hodn.</span>
                                        </div>
                        </div>
                </div>
        </article>

        <article id="highlight-8630" class="article article-poster-60">
                <figure class="article-img">
                        <a href="/film/8630-chyt-me-kdyz-to-dokazes/" title="Chyť mě, když to dokážeš">
                                <img src="//image.pmgstatic.com/cache/resized/w60h85/files/images/film/posters/162/402/162402961_652692.jpg" loading="lazy" width="59" height="85" srcset="//image.pmgstatic.com/cache/resized/w60h85/files/images/film/posters/162/402/162402961_652692.jpg 1x, //image.pmgstatic.com/cache/resized/w120h170/files/images/film/posters/162/402/162402961_652692.jpg 2x, //image.pmgstatic.com/cache/resized/w180h255/files/images/film/posters/162/402/162402961_652692.jpg 3x" alt="Chyť mě, když to dokážeš">
                        </a>
                </figure>
                <div class="article-content article-content-toplist">
                        <header class="article-header">
                                <h3 class="film-title-norating">
                                        <span class="film-title-user">
                                                101.
                                        </span>
                                        <a href="/film/8630-chyt-me-kdyz-to-dokazes/" title="Chyť mě, když to dokážeš" class="film-title-name">
                                                Chyť mě, když to dokážeš
                                        </a>
                                        <span class="film-title-info">
                                                <span class="info">(2002)</span>
                                        </span>
                                </h3>
                        </header>

    """

    title: str
    path: str
    actors: List[ActorData]
    id: int

    @classmethod
    async def from_node(cls, node: bs4.element.Tag, full_info=False):
        title_node = node.find("a", {"class": "film-title-name"})
        title = title_node.get("title")
        path = title_node.get("href")

        if full_info:
            movie_url = url_join(CSFD_URL, path)
            content = await send_request_async(movie_url)
            movie = parse_movie_page(content)
            movie.path = path

        actors = []

        creators_nodes = node.find_all("p", {"class": "film-creators"})
        for child in creators_nodes:
            if child.getText().startswith("Hrají:"):
                actors = [ActorData.from_node(a_node) for a_node in child.find_all("a")]
                break

        return MovieData(title, path, actors, -1)

    def as_dict(self):
        result = dict(
            title=self.title, url=url_join(CSFD_URL, self.path), actors=[actor.as_dict() for actor in self.actors]
        )
        if self.id > 0:
            result["id"] = self.id
        return result


def parse_movie_page(content) -> MovieData:
    soup = bs4.BeautifulSoup(content, "lxml")

    movie_info = soup.find("body").find("div", {"class": "main-movie"}).find("div", {"class": "film-info"})
    movie_header = movie_info.find("header", {"class": "film-header"})

    title_node = movie_header.find("div", {"class": "film-header-name"}).find("h1")
    title = title_node.getText().strip()

    actors = []
    creators_nodes = movie_info.find("div", {"class": "creators"}).find_all("div")
    for child in creators_nodes:
        text_node = child.find("h4")
        if text_node.getText().startswith("Hrají:"):
            actors = [ActorData.from_node(a_node) for a_node in child.find_all("a")]
            break

    return MovieData(title, "", actors, -1)


async def parse_page(content, pages=False, *, all_actors=False) -> Tuple[List[MovieData], List[PageData]]:
    """
    <div class="box-content box-content-striped-articles">
        <div class="box-more-bar box-more-bar-charts">
            <a href="/zebricky/filmy/nejlepsi/">1</a>
            <a href="/zebricky/filmy/nejlepsi/?from=100">100</a>
            <a href="/zebricky/filmy/nejlepsi/?from=200">200</a>
            <span class="current">300</span>
            <a href="/zebricky/filmy/nejlepsi/?from=400">400</a>
            <a href="/zebricky/filmy/nejlepsi/?from=500">500</a>
            <a href="/zebricky/filmy/nejlepsi/?from=600">600</a>
            <a href="/zebricky/filmy/nejlepsi/?from=700">700</a>
            <a href="/zebricky/filmy/nejlepsi/?from=800">800</a>
            <a href="/zebricky/filmy/nejlepsi/?from=900">900</a>
        </div>


    </div>
    """
    soup = bs4.BeautifulSoup(content, "lxml")

    _movies, _pages = [], []
    if articles_node := soup.find("body").find("div", {"class": "box-content-striped-articles"}):
        if pages:
            _pages = [
                PageData.from_node(a_node)
                for a_node in articles_node.find("div", {"class": "box-more-bar box-more-bar-charts"}).find_all("a")
            ]

        _movies = [await MovieData.from_node(a_node, all_actors) for a_node in articles_node.find_all("article")]

    return _movies, _pages


async def main(commander, *args, **options):

    # get pages & movies objects
    count = options["count"]

    # send first request
    first_url = url_join(CSFD_URL, CSFD_BEST_MOVIES_PATH)
    content = await send_request_async(first_url)
    full_actors = options.get("full_actors", False)

    # send
    movies, pages = await parse_page(content, pages=True, all_actors=full_actors)
    for page in pages:
        page_url = url_join(CSFD_URL, page.path)
        content = await send_request_async(page_url)
        page_movies, _n = await parse_page(content, all_actors=full_actors)
        movies.extend(page_movies)

        if len(movies) >= count:
            movies = movies[:count]
            break

    return movies


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("--count", required=False, type=int, default=300)
        parser.add_argument("--clear-database", action="store_true")
        parser.add_argument("--set-default-password", action="store_true")
        parser.add_argument("--full-actors", action="store_true")

    def handle(self, *args, **options):
        if options.get("clear_database"):
            call_command("sqlflush")
            call_command("migrate")

            if options.get("set-default-password"):
                admin = User.objects.get(username="admin")
                admin.set_password("admin")

                staff = User.objects.get(username="admin")
                staff.set_password("staff")

        movies = asyncio.run(main(self, *args, **options))

        # save to database
        # insert actors
        all_actors = dict()  # temp actor list

        # remove actor duplicity
        for movie in movies:
            all_actors.update({actor.fullName: actor for actor in movie.actors})

        for actor in all_actors.values():
            actor_record, created = Actor.objects.get_or_create(fullName=actor.fullName, defaults=actor.as_dict())
            if not created:
                actor_record.save()

            actor.id = actor_record.id

        self.stdout.write(self.style.SUCCESS("Successfully parse and dumps %d actors" % len(all_actors)))

        # insert movies
        for movie in movies:
            movie_default = movie.as_dict()
            movie_default.pop("actors")

            movie_record, created = Movie.objects.get_or_create(title=movie.title, defaults=movie_default)
            if not created:
                movie_record.save()

            movie.id = movie_record.id

            # insert many to many
            for actor in movie.actors:
                movie_record.actors.add(all_actors[actor.fullName].id)
            movie_record.save()

        self.stdout.write(self.style.SUCCESS("Successfully parse and dumps %d movies" % len(movies)))
