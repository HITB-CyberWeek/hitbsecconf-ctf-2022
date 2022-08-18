using App.Models;
using App.Repositories;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using MongoDB.Driver;

namespace App
{
    public class Startup
    {
        public void ConfigureServices(IServiceCollection services)
        {
            services.AddSingleton<IConfiguration>(sp =>
                new ConfigurationBuilder()
                    .AddJsonFile("appsettings.json")
                    .AddEnvironmentVariables()
                    .Build());

            services.AddSingleton(sp =>
            {
                var connectionString = sp.GetRequiredService<IConfiguration>().GetConnectionString("MongoDb");
                var mongoUrl = new MongoUrl(connectionString);
                var mongoClient = new MongoClient(MongoClientSettings.FromUrl(mongoUrl));
                return mongoClient.GetDatabase(mongoUrl.DatabaseName);
            });

            services.AddSingleton(sp =>
                sp.GetRequiredService<IMongoDatabase>().GetCollection<UserMongoDocument>("users"));
            services.AddSingleton(sp =>
                sp.GetRequiredService<IMongoDatabase>().GetCollection<NoteMongoDocument>("notes"));

            services.AddSingleton<IUserRepository, UserRepository>();
            services.AddSingleton<INoteRepository, NoteRepository>();
            services.AddSingleton<IAuthenticationService, AuthenticationService>();

            services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
                .AddCookie(CookieAuthenticationDefaults.AuthenticationScheme,
                    options => { options.LoginPath = new PathString("/login"); });

            services.AddAuthorization(options =>
            {
                options.FallbackPolicy = new AuthorizationPolicyBuilder()
                    .RequireAuthenticatedUser()
                    .Build();
            });

            services.AddMvc();

            services.Configure<ForwardedHeadersOptions>(options =>
            {
                options.ForwardedHeaders = ForwardedHeaders.XForwardedProto;
            });
        }

        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            app.UseForwardedHeaders();
            app.UseRouting();
            app.UseAuthentication();
            app.UseAuthorization();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllerRoute("admin", "{controller=Admin}/{action=Export}")
                    .RequireHost(Constants.AdminHost);
                endpoints.MapControllerRoute("default", "{controller=Notes}/{action=Index}");
            });
        }
    }
}