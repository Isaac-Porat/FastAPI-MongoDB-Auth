"use client";

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import { Button } from '@/components/ui/button';

// Allow the user to access the admin page or the user page
// TODO: Need to fix the routing and the backend token validation with the get_current_active_user function

function Dashboard() {
  const router = useRouter()

  const [accessToken, setAccessToken] = useState('');

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');
    setAccessToken(accessToken);

    // console.log(accessToken)

    // const getData = async () => {
    //   try {
    //     const response = await axios.get('http://localhost:8000/users/me', {}, {
    //       headers: {
    //         'Authorization': `Bearer ${accessToken}`
    //     }
    //   });
    //   console.log(response);
    //   if (response.status === 200) {
    //     console.log("Stay on page");
    //   } else {
    //     router.push('http://localhost:3000/');
    //   }

    //   } catch (error) {
    //     if (axios.isAxiosError(error)) {
    //       console.log(error);
    //       console.error(error.response);
    //       router.push('http://localhost:3000/');
    //     } else {
    //       console.error(error);
    //       router.push('http://localhost:3000/');
    //     }
    //   }
    // }
    // getData();
  }, []);

  return (
    <div className='flex justify-center items-center h-screen'>
      <Card className="w-[350px] h-[200px]">
        <CardHeader>
          <CardTitle>Account</CardTitle>
        </CardHeader>
        <CardContent>
          <CardDescription className="block w-full overflow-hidden whitespace-nowrap text-ellipsis pass">
            User token: <span className="password-style">{accessToken ? accessToken : "None"}</span>
          </CardDescription>
        </CardContent>
        <CardFooter className="flex justify-between mx-10">
          <Link
            href="/admin"
          >
            <Button variant='outline'>
              Admin
            </Button>
          </Link>
        </CardFooter>
      </Card>
    </div>
  );

}

export default Dashboard;
