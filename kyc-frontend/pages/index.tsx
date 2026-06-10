/** Root Index Page - redirects to login or dashboard */
import type { NextPage } from "next";
import { useEffect } from "react";
import { useRouter } from "next/router";
import { useAppSelector } from "../store/hooks";

const IndexPage: NextPage = () => {
  const router = useRouter();
  const { token } = useAppSelector((state) => state.auth);

  useEffect(() => {
    if (token) {
      router.push("/dashboard");
    } else {
      router.push("/login");
    }
  }, [router, token]);

  return null;
};

export default IndexPage;