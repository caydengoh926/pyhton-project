
def get_bread_crumb(category):

    breadcrumb={
        'cat1':'',
        'cat2':'',
        'cat3':''
    }
    if category.parent == None:
        breadcrumb['cat']= category
    elif category.subs.count() == 0 :
        cat2 = category.parent
        breadcrumb['cat1']= cat2.parent
        breadcrumb['cat2']= cat2
        breadcrumb['cat3']= category
    else:
        breadcrumb['cat1']= category.parent
        breadcrumb['cat2']= category

    return breadcrumb