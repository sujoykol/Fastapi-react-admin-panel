import api from "../api/axios";

const adminService = {
  getMe: async () => {
    const response = await api.get("/auth/me");

    return response.data;
  },
};

export default adminService;