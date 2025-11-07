import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";

export default function ModuleDetail() {
  const { module } = useParams();
  const [routes, setRoutes] = useState([]);

  useEffect(() => {
    // Example: Fetch module endpoints from backend OpenAPI schema
    axios.get("http://127.0.0.1:8000/openapi.json").then((res) => {
      const allRoutes = Object.keys(res.data.paths)
        .filter((p) => p.includes(`/api/${module}`))
        .map((p) => ({ path: p, methods: Object.keys(res.data.paths[p]) }));
      setRoutes(allRoutes);
    });
  }, [module]);

  return (
    <div className="p-10 bg-gray-50 min-h-screen">
      <h1 className="text-4xl font-bold text-center mb-8 capitalize">{module} Module</h1>

      {routes.length === 0 ? (
        <p className="text-center text-gray-500">Loading endpoints...</p>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {routes.map((r, i) => (
            <div key={i} className="p-6 bg-white rounded-xl shadow hover:shadow-lg">
              <h3 className="font-semibold text-lg text-gray-800 mb-2">{r.path}</h3>
              <p className="text-sm text-gray-500">Methods: {r.methods.join(", ")}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
