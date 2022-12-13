from dataclasses import dataclass
from typing import List, Tuple

import bs4
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from api.utils import send_request, url_join
from api.models import Actor, Movie, MovieActor


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
        split_name = self.fullName.split(' ')
        result = dict(
            givenName=split_name[0],
            lastName=split_name[-1],
            fullName=self.fullName,
            url=url_join(CSFD_URL, self.path)
        )
        if self.id > 0:
            result["id"] = self.id
        return result

@dataclass
class MovieInfo:
    path: str
    
    
    
    
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
    def from_node(cls, node: bs4.element.Tag, full_info=False):
        title_node = node.find("a", {"class": "film-title-name"})
        title = title_node.get("title")
        path = title_node.get("href")
        
        # actors
        actors = []
        if full_info:
            movie_url = url_join(CSFD_URL, path)
            content = send_request(movie_url)
            parse_movie_page(content)
        else:
            creators_nodes = node.find_all("p", {"class": "film-creators"})
            for child in creators_nodes:
                if child.getText().startswith("Hrají:"):
                    actors = [
                        ActorData.from_node(a_node) for a_node in child.find_all("a")
                    ]
                
        return MovieData(title, path, actors, -1)
    
    def as_dict(self):
        result = dict(
            title=self.title,
            url=url_join(CSFD_URL, self.path),
            actors=[actor.as_dict() for actor in self.actors]
        )
        if self.id > 0:
            result["id"] = self.id
        return result


def parse_movie_page(content):
    soup = bs4.BeautifulSoup(content, 'lxml')
    
    # if articles_node := soup.find("body").find("div", {"class": "box-content-striped-articles"}):
    
    
    
    
def parse_page(content, pages=False) -> Tuple[List[MovieData], List[PageData]]:
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
    soup = bs4.BeautifulSoup(content, 'lxml')
    
    _movies, _pages = [], []
    if articles_node := soup.find("body").find("div", {"class": "box-content-striped-articles"}):
        if pages:
            _pages = [
                PageData.from_node(a_node) for a_node in articles_node.find(
                    "div", {"class": "box-more-bar box-more-bar-charts"}).find_all("a")
                ]
        
        _movies = [MovieData.from_node(a_node) for a_node in articles_node.find_all("article")]
    
    return _movies, _pages


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('--count', required=False, type=int, default=300)
        parser.add_argument('--clear-database', action="store_true")

    def handle(self, *args, **options):
        
        if options.get("clear_database"):
            call_command("sqlflush")
            call_command("migrate")
        
        # get pages & movies objects
        count = options["count"]
        first_url = url_join(CSFD_URL, CSFD_BEST_MOVIES_PATH)
        content = send_request(first_url)
        movies, pages = parse_page(content, pages=True)
        for page in pages:
            page_url = url_join(CSFD_URL, page.path)
            content = send_request(page_url)
            page_movies, _n = parse_page(content)
            movies.extend(page_movies)
            
            if len(movies) >= count:
                movies = movies[:count]
                break
        
        # save to database
        # insert actors
        all_actors = dict() # temp actor list, remove duplicity
        
        # remove actor duplicity
        for movie in movies:
            all_actors.update({actor.fullName: actor for actor in movie.actors})
        
        for actor in all_actors.values():
            actor_record, created = Actor.objects.get_or_create(fullName=actor.fullName, defaults=actor.as_dict())
            if not created:
                actor_record.save()
            
            actor.id = actor_record.id
            
        
        self.stdout.write(self.style.SUCCESS('Successfully parse and dumps %d actors' % len(all_actors)))
        
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

        self.stdout.write(self.style.SUCCESS('Successfully parse and dumps %d movies' % len(movies)))