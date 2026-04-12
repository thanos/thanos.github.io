

 After you clone
 Go into the repo
 
 cd thanos
 Use a current Node.js (the repo’s .tool-versions lists 25.6.1 for asdf; Node 20+ is fine if you don’t use asdf.)
 
 Install dependencies
 
 npm install
 Run the dev server (edit with hot reload)
 
 npm run dev
 Open the URL it prints (usually http://localhost:4321).
 
 Production build (output in dist/)
 
 npm run build
 Preview the production build locally (optional)
 
 npm run preview
 Notes
 
 No .env is required for a normal local build unless you add secrets later.
 If you use asdf: asdf install in the repo (reads .tool-versions), then the same npm install / npm run build steps.
 pnpm/yarn aren’t configured here; this project expects npm and package-lock.json.
