from canteen.models import Review


def submit_review(user, meal, stars: int, comment: str):
    review = get_review_for_user_and_meal(user, meal)
    if review is None:
        review = Review.objects.create(
            user=user, meal=meal, stars=stars, comment=comment
        )
    else:
        review.stars = stars
        review.comment = comment
        review.save()
    return review


def get_review_for_user_and_meal(user, meal):
    review = Review.objects.filter(user=user, meal=meal).first()
    return review
