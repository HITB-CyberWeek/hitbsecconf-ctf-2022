using System.Threading.Tasks;
using App.Repositories;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;

namespace App.Controllers
{
    [AllowAnonymous]
    [Host(Constants.AdminHost)]
    public class AdminController : Controller
    {
        private readonly INoteRepository _repository;

        public AdminController(INoteRepository repository)
        {
            _repository = repository;
        }

        [Route("/export")]
        public async Task<IActionResult> Export()
        {
            var notes = await _repository.GetAllAsync();
            return Json(notes);
        }
    }
}