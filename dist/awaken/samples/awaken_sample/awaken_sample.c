#include "stdlib.h"
#include "stdio.h"
#include <windows.h>
#include <conio.h>
#include <errno.h>
#include <WinDef.h>

#include "../../include/msp_cmn.h"
#include "../../include/qivw.h"
#include "../../include/msp_errors.h"

#pragma comment(lib, "winmm.lib")  

 #ifdef _WIN64
 #pragma comment(lib,"../../libs/msc_x64.lib")
 #else
 #pragma comment(lib, "../../libs/msc.lib")
 #endif

//读取文件
#define IVW_AUDIO_FILE_NAME "audio/awake.pcm"
#define FRAME_LEN	640 //16k采样率的16bit音频，一帧的大小为640B, 时长20ms

int wakeupFlage = 0;
void sleep_ms(int ms)
{
	Sleep(ms);
}

int cb_ivw_msg_proc( const char *sessionID, int msg, int param1, int param2, const void *info, void *userData )
{
	if (MSP_IVW_MSG_ERROR == msg) //唤醒出错消息
	{
		printf("\n\nMSP_IVW_MSG_ERROR errCode = %d\n\n", param1);
	}
	else if (MSP_IVW_MSG_WAKEUP == msg) //唤醒成功消息
	{
		printf("\n\nMSP_IVW_MSG_WAKEUP result = %s\n\n", info);
		wakeupFlage = 1;
	}
	return 0;
}
//通过读取音频文件唤醒的demo
void run_ivw(const char *grammar_list, const char* audio_filename ,  const char* session_begin_params)
{
	const char *session_id = NULL;
	int err_code = MSP_SUCCESS;
	FILE *f_aud = NULL;
	long audio_size = 0;
	long real_read = 0;
	long audio_count = 0;
	int count = 0;
	int audio_stat = MSP_AUDIO_SAMPLE_CONTINUE;
	char *audio_buffer=NULL;
	char sse_hints[128];
	if (NULL == audio_filename)
	{
		printf("params error\n");
		return;
	}

	f_aud=fopen(audio_filename, "rb");
	if (NULL == f_aud)
	{
		printf("audio file open failed! \n\n");
		return;
	}
	fseek(f_aud, 0, SEEK_END);
	audio_size = ftell(f_aud);
	fseek(f_aud, 0, SEEK_SET);
	audio_buffer = (char *)malloc(audio_size);
	if (NULL == audio_buffer)
	{
		printf("malloc failed! \n");
		goto exit;
	}
	real_read = fread((void *)audio_buffer, 1, audio_size, f_aud);
	if (real_read != audio_size)
	{
		printf("read audio file failed!\n");
		goto exit;
	}

	session_id=QIVWSessionBegin(grammar_list, session_begin_params, &err_code);
	if (err_code != MSP_SUCCESS)
	{
		printf("QIVWSessionBegin failed! error code:%d\n",err_code);
		goto exit;
	}

	err_code = QIVWRegisterNotify(session_id, cb_ivw_msg_proc,NULL);
	if (err_code != MSP_SUCCESS)
	{
		_snprintf(sse_hints, sizeof(sse_hints), "QIVWRegisterNotify errorCode=%d", err_code);
		printf("QIVWRegisterNotify failed! error code:%d\n",err_code);
		goto exit;
	}
	while(1)
	{
		long len = 10*FRAME_LEN; //16k音频，10帧 （时长200ms）
		audio_stat = MSP_AUDIO_SAMPLE_CONTINUE;
		if(audio_size <= len)
		{
			len = audio_size;
			audio_stat = MSP_AUDIO_SAMPLE_LAST; //最后一块
		}
		if (0 == audio_count)
		{
			audio_stat = MSP_AUDIO_SAMPLE_FIRST;
		}

		printf("csid=%s,count=%d,aus=%d\n",session_id, count++, audio_stat);
		err_code = QIVWAudioWrite(session_id, (const void *)&audio_buffer[audio_count], len, audio_stat);
		if (MSP_SUCCESS != err_code)
		{
			printf("QIVWAudioWrite failed! error code:%d\n",err_code);
			_snprintf(sse_hints, sizeof(sse_hints), "QIVWAudioWrite errorCode=%d", err_code);
			goto exit;
		}
		if (MSP_AUDIO_SAMPLE_LAST == audio_stat)
		{
			break;
		}
		audio_count += len;
		audio_size -= len;

		sleep_ms(200); //模拟人说话时间间隙，10帧的音频时长为200ms
	}
	_snprintf(sse_hints, sizeof(sse_hints), "success");

exit:
	if (NULL != session_id)
	{
		QIVWSessionEnd(session_id, sse_hints);
	}
	if (NULL != f_aud)
	{
		fclose(f_aud);
	}
	if (NULL != audio_buffer)
	{
		free(audio_buffer);
	}
}


//麦克风录入demo
void ivw_demo_microphone(const char *grammar_list, const char* session_begin_params)
{
	const char *session_id = NULL;
	int err_code = MSP_SUCCESS;
	long audio_size = 0;
	long audio_count = 0;
	int count = 0;
	int audio_stat = MSP_AUDIO_SAMPLE_CONTINUE;
	char sse_hints[128];
	DWORD bufsize;
	long len =0;

	HWAVEIN hWaveIn;  //输入设备
	WAVEFORMATEX waveform; //采集音频的格式，结构体
	BYTE *pBuffer;//采集音频时的数据缓存
	WAVEHDR wHdr; //采集音频时包含数据缓存的结构体
	HANDLE          wait;

	waveform.wFormatTag = WAVE_FORMAT_PCM;//声音格式为PCM
	waveform.nSamplesPerSec = 16000;//音频采样率
	waveform.wBitsPerSample = 16;//采样比特
	waveform.nChannels = 1;//采样声道数
	waveform.nAvgBytesPerSec = 16000;//每秒的数据率
	waveform.nBlockAlign = 2;//一个块的大小，采样bit的字节数乘以声道数
	waveform.cbSize = 0;//一般为0

	wait = CreateEvent(NULL, 0, 0, NULL);
	//使用waveInOpen函数开启音频采集
	waveInOpen(&hWaveIn, WAVE_MAPPER, &waveform, (DWORD_PTR)wait, 0L, CALLBACK_EVENT);

	bufsize= 1024 * 500;//开辟适当大小的内存存储音频数据，可适当调整内存大小以增加录音时间，或采取其他的内存管理方案

	session_id = QIVWSessionBegin(grammar_list, session_begin_params, &err_code);
	if (err_code != MSP_SUCCESS)
	{
		printf("QIVWSessionBegin failed! error code:%d\n", err_code);
		goto exit;
	}

	err_code = QIVWRegisterNotify(session_id, cb_ivw_msg_proc, NULL);
	if (err_code != MSP_SUCCESS)
	{
		_snprintf(sse_hints, sizeof(sse_hints), "QIVWRegisterNotify errorCode=%d", err_code);
		printf("QIVWRegisterNotify failed! error code:%d\n", err_code);
		goto exit;
	}

	pBuffer = malloc(bufsize);
	wHdr.lpData = (LPSTR)pBuffer;
	wHdr.dwBufferLength = bufsize;
	wHdr.dwBytesRecorded = 0;
	wHdr.dwUser = 0;
	wHdr.dwFlags = 0;
	wHdr.dwLoops = 1;
	waveInPrepareHeader(hWaveIn, &wHdr, sizeof(WAVEHDR));//准备一个波形数据块头用于录音
	waveInAddBuffer(hWaveIn, &wHdr, sizeof(WAVEHDR));//指定波形数据块为录音输入缓存
	waveInStart(hWaveIn);//开始录音

	//while (audio_count< bufsize && wakeupFlage!=1)//单次唤醒
	while (audio_count< bufsize)//持续唤醒
	{
		Sleep(200);//等待声音录制5s

		len = 10 * FRAME_LEN; //16k音频，10帧 （时长200ms）
		audio_stat = MSP_AUDIO_SAMPLE_CONTINUE;
		if (audio_count >= wHdr.dwBytesRecorded)
		{
			len = audio_size;
			audio_stat = MSP_AUDIO_SAMPLE_LAST; //最后一块
		}
		if (0 == audio_count)
		{
			audio_stat = MSP_AUDIO_SAMPLE_FIRST;
		}

		printf("csid=%s,count=%d,aus=%d\n", session_id, count++, audio_stat);
		err_code = QIVWAudioWrite(session_id, (const void *)&pBuffer[audio_count], len, audio_stat);
		if (MSP_SUCCESS != err_code)
		{
			printf("QIVWAudioWrite failed! error code:%d\n", err_code);
			_snprintf(sse_hints, sizeof(sse_hints), "QIVWAudioWrite errorCode=%d", err_code);
			goto exit;
		}
		if (MSP_AUDIO_SAMPLE_LAST == audio_stat)
		{
			break;
		}
		audio_count += len;
	}
	waveInReset(hWaveIn);//停止录音
	if (NULL != pBuffer) 
	{
		free(pBuffer);
	}
	_snprintf(sse_hints, sizeof(sse_hints), "success");

exit:
	if (NULL != session_id)
	{
		QIVWSessionEnd(session_id, sse_hints);
	}

}

int main(int argc, char* argv[])
{
	int         ret       = MSP_SUCCESS;
	const char *lgi_param = "appid = 316e9b7a, work_dir = .";
	const char *ssb_param = "ivw_threshold=0:1450,sst=wakeup,ivw_res_path =fo|res/ivw/wakeupresource.jet";
	int aud_src = 0;
	/* 用户登录 */
	ret = MSPLogin(NULL, NULL, lgi_param); //第一个参数是用户名，第二个参数是密码，第三个参数是登录参数，用户名和密码可在http://www.xfyun.cn注册获取
	if (MSP_SUCCESS != ret)
	{
		printf("MSPLogin failed, error code: %d.\n", ret);
		goto exit ;//登录失败，退出登录
	}
	printf("\n###############################################################################################################\n");
	printf("## ivw_demo_microphone 为使用麦克风进行唤醒的demo,run_ivw为使用音频文件唤醒的demo，请选择其中一种方式进行唤醒##\n");
	printf("## 请注意，在使用run_ivw唤醒语音需要根据唤醒词内容自行录制并重命名为宏IVW_AUDIO_FILE_NAME所指定名称，存放在bin/audio文件里##\n");
	printf("###############################################################################################################\n\n");
	
	printf("音频数据在哪? \n0: 从文件读入\n1:从MIC说话\n");
	scanf("%d", &aud_src);
	if (aud_src) 
	{
		ivw_demo_microphone(NULL, ssb_param);
	}
	else
	{
		run_ivw(NULL, IVW_AUDIO_FILE_NAME, ssb_param);  
	}

	sleep_ms(2000);
exit:
	printf("按任意键退出 ...\n");
	_getch();
	MSPLogout(); //退出登录
	return 0;
}
