using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;

namespace App.Controllers
{
    public class UserController : Controller
    {
        public IActionResult Index()
        {
            return Content("Public info");
        }
    }
}
