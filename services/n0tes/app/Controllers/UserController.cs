using Microsoft.AspNetCore.Mvc;

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
