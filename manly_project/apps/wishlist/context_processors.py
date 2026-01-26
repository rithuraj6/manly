def wishlist_count(request):
    if request.user.is_authenticated:
        wishlist = getattr(request.user, "wishlist", None)
        if wishlist:
            return {
                "wishlist_count": wishlist.items.count()
            }
    return {"wishlist_count": 0}
