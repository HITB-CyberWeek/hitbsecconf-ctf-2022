using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;

namespace App.Controllers
{
    [Host("admin.n0tes.hitb.org")]
    public class AdminController : Controller
    {
        public IActionResult Index()
        {
            return Content("Secret flag");
        }
    }
}
