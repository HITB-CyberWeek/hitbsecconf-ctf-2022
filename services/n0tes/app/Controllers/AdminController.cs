using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;

namespace App.Controllers
{
   
    [Host(Constants.AdminHost)]
    public class AdminController : Controller
    {
        public IActionResult Index()
        {
            return Content("Secret flag");
        }
    }
}
