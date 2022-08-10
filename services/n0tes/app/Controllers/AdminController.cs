using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;

namespace App.Controllers
{
    [AllowAnonymous]
    [Host(Constants.AdminHost)]
    public class AdminController : Controller
    {
        public IActionResult Index()
        {
            return Content("Secret flag");
        }
    }
}
