"use client";

// TODO:
// Add admin login and ability to use other CRUD functions

import axios from 'axios';
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from 'zod';
import { useState, useEffect } from 'react';

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

const userSchema = z.object({
  username: z.string().min(1).max(20).trim(),
  password: z.string().min(8).regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\w\W]{8,}$/),
});

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [authStatus, setAuthStatus] = useState("");

  const postData = async (user: z.infer<typeof userSchema>) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('username', user.username);
      formData.append('password', user.password);
      const response = await axios.post('http://localhost:8000/register', formData);
      console.log(response)
      setAuthStatus("Account created successfully.")

    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.log(error)
        console.error(error.response);
        if (error.response?.status === 400) {
          setAuthStatus("Username already exists.");
        }
      } else {
        console.error(error);
      }
    }
    setLoading(false);
  };

  const form = useForm<z.infer<typeof userSchema>>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  })

  function onSubmit(values: z.infer<typeof userSchema>) {
    postData(values);
  }

  return (
    <div className='flex justify-center items-center h-screen'>
      <Card className="w-[350px]">
        <CardHeader>
          <CardTitle>Create a new account</CardTitle>
          {/* <CardDescription>Deploy your new project in one-click.</CardDescription> */}
        </CardHeader>
        <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Username</FormLabel>
                  <FormControl>
                    <Input placeholder="john" {...field} />
                  </FormControl>
                  <FormDescription>
                    This is your public username.
                  </FormDescription>
                  {authStatus && (
                      <FormMessage>
                        <div className="text-red-500">{authStatus}</div>
                      </FormMessage>
                    )}
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder="Enter your password" {...field} />
                  </FormControl>
                  <FormDescription>
                    Choose a strong password to keep your account secure.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <CardFooter className="flex justify-between">
              <Button
                type="submit"
                disabled = {loading}
              >
                {loading ? 'Loading...' : 'Submit'}
              </Button>
            </CardFooter>
          </form>
        </Form>
        </CardContent>
      </Card>
    </div>
  )
}
