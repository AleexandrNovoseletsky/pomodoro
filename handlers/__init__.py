from handlers.categories import router as categories_router
from handlers.tasks import router as tasks_router
from handlers.users import router as user_router

routers = (categories_router, tasks_router, user_router)
